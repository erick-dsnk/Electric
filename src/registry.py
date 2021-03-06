######################################################################
#                              REGISTRY                              #
######################################################################

from Classes.RegSnapshot import RegSnapshot
import difflib
import winreg


keys = []

def get_uninstall_key(package_name : str, display_name: str):
    def send_query(hive, flag):
        aReg = winreg.ConnectRegistry(None, hive)
        aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                            0, winreg.KEY_READ | flag)

        count_subkey = winreg.QueryInfoKey(aKey)[0]

        software_list = []

        for i in range(count_subkey):
            software = {}
            try:
                asubkey_name = winreg.EnumKey(aKey, i)
                asubkey = winreg.OpenKey(aKey, asubkey_name)
                software['DisplayName'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]
                try:
                    software['UninstallString'] = winreg.QueryValueEx(asubkey, "UninstallString")[0]
                except:
                    software['UninstallString'] = 'undefined'
                try:
                    software['Version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
                except EnvironmentError:
                    software['Version'] = 'undefined'
                try:
                    software['Publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
                except EnvironmentError:
                    software['Publisher'] = 'undefined'
                software_list.append(software)
            except EnvironmentError:
                continue

        return software_list

    keys = send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + send_query(winreg.HKEY_CURRENT_USER, 0)
    
    final_array = []
    total = []

    def get_uninstall_string(package_name : str):
        nonlocal final_array
        string_gen(package_name)

        for key in keys:
            display_name = key['DisplayName']
            url = None if 'URLInfoAbout' not in key else key['URLInfoAbout']
            uninstall_string = '' if 'UninstallString' not in key else key['UninstallString']
            quiet_uninstall_string = '' if 'QuietUninstallString' not in key else key['QuietUninstallString']
            install_location = None if 'InstallLocation' not in key else key['InstallLocation']
            final_list = [display_name, url, uninstall_string, quiet_uninstall_string, install_location]
            index = 0
            matches = None
            refined_list = []

            for item in final_list:
                if item is None:
                    final_list.pop(index)
                else:
                    name = item.lower()

                refined_list.append(name)
                index += 1
                
            for string in strings:
                matches = difflib.get_close_matches(string, refined_list)
                if not matches:
                    possibilities = []

                    for element in refined_list:
                        for string in strings:
                            if string in element:
                                possibilities.append(key)

                    if possibilities:
                        total.append(possibilities)
                        
                    else:
                        continue
                else:
                    final_array.append(key)

    strings = []

    def string_gen(package_name : str):
        package_name = package_name.split('-')
        strings.append(''.join(package_name))
        strings.append(display_name.lower())

    def get_more_accurate_matches(return_array):
        index, confidence = 0, 50
        final_index, final_confidence = (None, None)

        for key in return_array:
            name = key['DisplayName']
            loc = None
            try:
                loc = key['InstallLocation']
            except KeyError:
                pass
    
            uninstall_string = None if 'UninstallString' not in key else key['UninstallString']
            quiet_uninstall_string = None if 'QuietUninstallString' not in key else key['QuietUninstallString']
            url = None if 'URLInfoAbout' not in key else key['URLInfoAbout']

            for string in strings:
                if name:
                    if string.lower() in name.lower():
                        confidence += 10
                if loc:
                    if string.lower() in loc.lower():
                        confidence += 5
                if uninstall_string:
                    if string.lower() in uninstall_string.lower():
                        confidence += 5
                if quiet_uninstall_string:
                    if string.lower() in quiet_uninstall_string.lower():
                        confidence += 5
                if url:
                    if string.lower() in url.lower():
                        confidence += 10

                if final_confidence == confidence:
                    word_list = package_name.split('-')

                    for word in word_list:
                        for key in [name, quiet_uninstall_string, loc, url]:
                            if key:
                                if word in key:
                                    confidence += 5

                        if word:
                            if uninstall_string:
                                if word in uninstall_string:
                                        confidence += 5

                if not final_index and not final_confidence:
                    final_index = index
                    final_confidence = confidence
                if final_confidence < confidence:
                    final_index = index
                    final_confidence = confidence
            index += 1
        return return_array[final_index]


    get_uninstall_string(package_name)


    if final_array:
        if len(final_array) > 1:
            return get_more_accurate_matches(final_array)
        return final_array
    return_array = []
    for something in total:
        return_array.append(something[0])
    if len(return_array) > 1:
        return get_more_accurate_matches(return_array)
    else:
        return return_array


def get_environment_keys() -> RegSnapshot:
    env_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ)
    sys_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, R'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_READ)
    sys_idx = 0
    while True:
        if winreg.EnumValue(env_key, sys_idx)[0] == 'Path':
            break
        sys_idx += 1
    env_idx = 0
    while True:
        if winreg.EnumValue(sys_key, env_idx)[0] == 'Path':
            break
        env_idx += 1
    snap = RegSnapshot(str(winreg.EnumValue(env_key, sys_idx)[1]), len(str(winreg.EnumValue(env_key, sys_idx)[1]).split(';')), str(winreg.EnumValue(sys_key, env_idx)[1]), len(str(winreg.EnumValue(sys_key, env_idx)[1]).split(';')))
    return snap
