from subprocess import *
from utils import *
from external import *
from sys import platform
import click


class Config:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.publisher = dictionary['Info'][0]['Publisher']
        self.description = dictionary['Info'][1]['Description']
        self.os = dictionary['Info'][2]['OS']
        self.headers = dictionary.keys()

    def check_prerequisites(self):
        dictionary = self.dictionary
        headers = dictionary.keys()
        
        if 'Info' in headers:
           
            click.echo(click.style(f'Publisher => {self.publisher}'))
            click.echo(click.style(f'Description => {self.description}', fg='yellow'))    
        
            if platform == 'win32' and not self.os == 'Windows':
                
                if not click.confirm(f'WARNING: This Config Has A Target OS Of {self.os}. Would you like to continue?'):
                    exit()

        if 'Pip-Packages' in headers:
                try:
                    Popen('pip', stdin=PIPE, stdout=PIPE, stderr=PIPE)
                except FileNotFoundError:
                    
                    click.echo(click.style('Pip Not Found, Aborting Config Installation!', fg='red'))
                    exit()

        if 'Node-Packages' in headers:
                try:
                   Popen('npm', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                except FileNotFoundError:
                    
                    click.echo(click.style('Node Not Found, Aborting Config Installation!', fg='red'))
                    exit()
        editor_type = self.dictionary['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
        if editor_type:
            if not find_existing_installation(editor_type, 'Visual Studio Code'):
                click.echo(click.style('Visual Studio Code Not Found, Aborting Config Installation!', fg='red'))
            else:
                if editor_type == 'Visual Studio Code':
                    try:
                        Popen('code --help', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                    except FileNotFoundError:
                        click.echo(click.style('Visual Studio Code Found But Shell Extension Not Found, Aborting Config Installation!', fg='red'))

        click.echo(click.style('All Tests Passed!', 'green'))

    @staticmethod
    def generate_configuration(filepath: str):
        d = {}
        with open(f'{filepath}', 'r') as f:
            chunks = f.read().split("[")

            for chunk in chunks:
                chunk = chunk.replace("=>", ":").split('\n')
                header = chunk[0].replace("[", '').replace(']', '').strip()
                d[header] = []

                for line in chunk[1:]:
                    if line and '#' not in line:
                        try:
                            k, v = line.split(":")
                            k, v = k.strip(), v.strip()
                            if v == '':
                                with open(f'{filepath}', 'r') as f:
                                    lines = f.readlines()
                                ln_number = 0
                                idx = 0
                                for val in lines:
                                    if val.strip() == line.replace(':', '=>').strip():
                                        ln_number = idx
                                    idx += 1
                                click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                message = line.replace(':', '')
                                click.echo(click.style(f'ValueNotFoundError : No Value Provided For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                exit()
                        except ValueError:
                            if header in ['Packages', 'Pip-Packages', 'Editor-Extensions']:
                                k, v = line, "latest"           
                            else:
                                with open(f'{filepath}', 'r') as f:
                                    lines = f.readlines()

                                ln_number = 0
                                idx = 0
                                for val in lines:
                                    if val.strip() == line.replace(':', '=>').strip():
                                        ln_number = idx
                                    idx += 1

                                click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                message = line.replace(':', '')
                                click.echo(click.style(f'ValueNotFoundError : Expecting A Value Pair With `=>` Operator For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                exit()

                        d[header].append({ k : v.replace('"', '') })

        d.pop("")

        return Config(d)

    def install(self):
        config = self.dictionary
        python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
        node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
        editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
        packages = config['Packages'] if 'Packages' in self.headers else None
        editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
        for package in packages:
            try:
                os.system(f'electric install {list(package.keys())[0]}')
            except:
                if not click.confirm('Would you like to continue configuration installation?'):
                    exit()
        for python_package in python_packages:
            command = f'electric install --python {list(python_package.keys())[0]}'
            try:
                os.system(command)
            except:
                if not click.confirm('Would you like to continue configuration installation?'):
                    exit()
        
        if editor_type == 'Visual Studio Code':
            editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
            for extension in editor_extensions:
                extension = list(extension.keys())[0]
                command = f'electric install --vscode {extension}'
                try:
                    os.system(command)
                except:
                    if not click.confirm('Would you like to continue configuration installation?'):
                        exit()
        
        for node_package in node_packages:
            node_package = list(node_package)[0]
            try:
                os.system(f'electric install --node {node_package}')
            except:
                if not click.confirm('Would you like to continue configuration installation?'):
                    exit()


filepath = input('Enter the path to the .electric File => ').replace('\"', '')
config = Config.generate_configuration(filepath)
config.check_prerequisites()
config.install()
