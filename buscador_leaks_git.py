#! user/bin/python3

from git import Repo
import re
import signal
import sys

DIR_REPO = './skale-manager' # Dirección del repositorio en la carpeta local
KEY_WORDS = ['identification', 'username', 'password', 'key', 'login', 'credentials', 'private']
# Palabras de interés (posibles leaks de información delicada)

def extract(repo_dir):
    repo = Repo(repo_dir) # Cargamos el directorio
    branches_list = repo.branches # Sacamos una lista iterable con las ramas del directorio
    branch_names = [branch.name for branch in branches_list] # Obtenemos el nombre exacto de cada rama
    commit_list = [] # A esta lista se añadirán los commits
    for branch_name in branch_names: # Añadimos a la lista los commits de cada rama
        commit_list += list(repo.iter_commits(branch_name))
        # En este caso, el repositorio solo tiene una única rama ('develop')
    return commit_list

def transform(commit_list):
    wanted_commits = {} # A este diccionario añadiremos los commits que encontremos
    for commit in commit_list: # Buscamos las palabras deseadas en cada commit del directorio
        for key_word in KEY_WORDS: # En cada commit, buscamos cualquiera de las palabras deseadas
            if re.findall(key_word, commit.message, re.IGNORECASE) != []: # Si encuentra alguna de las palabras
                mensaje_commit = commit.message # Sacamos el mensaje de texto del commit
                clave = commit.hexsha # Obtenemos la clave de la información vinculada al commit
                wanted_commits[clave] = mensaje_commit # Añadimos ambos valores a un diccionario
    return wanted_commits

def load(wanted_commits):
    for clave in wanted_commits: # Mostramos por pantalla los commits encontrados
        print(f'Commit {clave}: {wanted_commits[clave]}')

def keyboard_interrupt(signal, frame): # Controlamos la posible interrupción voluntaria de la ejecución (Ctrl+C)
    print('\n Se ha interrumpido la búsqueda de commits con posibles leaks [!] \n')
    sys.exit()
signal.signal(signal.SIGINT, keyboard_interrupt)

if __name__ == '__main__':
    # Ejecutamos la ETL
    commit_list = extract(DIR_REPO)
    wanted_commits = transform(commit_list)
    load(wanted_commits)