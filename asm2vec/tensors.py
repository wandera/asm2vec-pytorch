import os
import shutil
import torch
import logging
from pathlib import Path

from asm2vec.train import train, load_model, load_data

logging.basicConfig(level=logging.INFO, format='%(message)s')


def move_files(abs_dirname, limit):
    """Moves files from a directory into subdirectories
    :param abs_dirname: absolute path to the directory
    :param limit: if the directory contains more that #limit files, they are split into subdirectories"""
    files = [os.path.join(abs_dirname, f) for f in os.listdir(abs_dirname) if not f.startswith('.')]
    if len(files) > limit:
        count = 0
        for f in files:
            if count % limit == 0:
                subdir_name = f'{abs_dirname}_{count // limit}'
                print(subdir_name)
                os.mkdir(subdir_name)

            f_base = os.path.basename(f)
            shutil.move(f, os.path.join(subdir_name, f_base))
            count += 1


def calc_tensors(asm_path: str, tensor_path: str, model_path: str, epochs: int, limit: int = 300,
                 device: str = 'cpu', learning_rate: float = 0.02) -> list:
    """
    Calculates vector representation of a binary as the mean per column of the vector representations of its assembly
    functions.
    :param asm_path: Path to folder with assembly function in a sub-folder per binary
    :param tensor_path: Path to folder to store the tensors
    :param model_path: Path to the trained model
    :param epochs: Number of epochs
    :param limit: if the directory contains more that #limit files, they are split into subdirectories
    :param device: 'auto' | 'cuda' | 'cpu'
    :param learning_rate: Learning rate
    :return: List of tensors
    """
    tensors_list = []
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    if os.path.isfile(model_path):
        model, tokens = load_model(model_path, device=device)
    else:
        print("No valid model")
        return []

    dir0 = Path(tensor_path)
    if not (os.path.exists(dir0)):
        os.mkdir(dir0)

    files = [f for f in os.listdir(asm_path) if (not f.startswith('.'))]
    for f in files:
        move_files(os.path.join(asm_path, f), limit)

    if os.path.isdir(asm_path):
        obj = os.scandir(asm_path)
        for entry in obj:
            if entry.is_dir() and os.listdir(entry) and entry.name:
                tensor_file = os.path.join(dir0, entry.name)
                if not (os.path.exists(tensor_file)):
                    functions, tokens_new = load_data([entry])
                    file_count = sum(len(files) for _, _, files in os.walk(entry))
                    tokens.update(tokens_new)
                    logging.info(f"Binary {entry.name}: {file_count} assembly functions")
                    model.update(file_count, tokens.size())
                    model = model.to(device)

                    model = train(
                        functions,
                        tokens,
                        model=model,
                        epochs=epochs,
                        device=device,
                        mode='update',
                        learning_rate=learning_rate
                    )

                    tensor = model.to('cpu').embeddings_f(torch.tensor([list(range(0, file_count))]))
                    tens = torch.squeeze(tensor)
                    if file_count == 1:
                        torch.save(tensor, tensor_file)
                    else:
                        torch.save(tens.mean(0), tensor_file)

    else:
        logging.info("No valid directory")

    tensors_full_list = [f[:40] for f in os.listdir(tensor_path) if (not f.startswith('.'))]
    tensors_list = list(set(tensors_full_list))

    for tensor in tensors_list:
        if tensors_full_list.count(tensor) > 1:
            tensor_list = [torch.load(Path(os.path.join(tensor_path, x))).detach().squeeze() for x in
                           os.listdir(tensor_path) if x[:40] == tensor]
            torch.save(torch.mean(torch.stack(tensor_list), dim=0), os.path.join(tensor_path, tensor))
            for fname in os.listdir(tensor_path):
                if fname.startswith(f"{tensor}_"):
                    os.remove(os.path.join(tensor_path, fname))

    return tensors_list
