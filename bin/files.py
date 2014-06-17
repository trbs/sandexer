import glob

class Fileformats():
    def __init__(self, cfg):
        self._cfg = cfg

        # extensions
        self.exts_movies = self._cfg.get('Fileformats', 'movies').split(',')
        self.exts_pictures = self._cfg.get('Fileformats', 'pictures').split(',')
        self.exts_documents = self._cfg.get('Fileformats', 'documents').split(',')
        self.exts_music = self._cfg.get('Fileformats', 'music').split(',')

        # fileformats
        self._list = {
            'Documents': 0,
            'Movies': 1,
            'Music': 2,
            'Pictures': 3
        }

    def get_format_from_id(self, id):
        for k,v in self._list.iteritems():
            if v == id:
                return k

    def get_format_from_string(self, string):
        try:
            return self._list[string]
        except KeyError:
            pass

    def get_fileformat(self, ext):
        format = 0

        if ext in self.exts_documents:
            format = 1
        elif ext in self.exts_movies:
            format = 2
        elif ext in self.exts_music:
            format = 3
        elif ext in self.exts_pictures:
            format = 4
        else:
            format = 0

        return format

class Icons():
    def __init__(self, cfg):
        self._cfg = cfg

        self.file_icons = {
            0: 'Very_Basic/file-128.png' ,
            1: 'Very_Basic/document-128.png',
            2: 'Photo_Video/film-128.png' ,
            3: 'Very_Basic/music-128.png' ,
            4: 'Very_Basic/picture-128.png'
        }

        self.additional_icons = [
            'Photo_Video/subs-128.png', #0 subtitles
            'Science/informatics-128.png', #1 nfo files
            'Operating_Systems/firefox_copyrighted-128.png', #2 firefox logo
            'Logos/adobe_photoshop_copyrighted-128.png', #3 photoshop
            'Logos/adobe_flash_copyrighted-128.png', #4 flash
            'Logos/adobe_illustrator_copyrighted-128.png', #5 illustrator
            'Programming/php-128.png', #6 PHP
            'Programming/python.png', #7 Python
            'Programming/java_coffee_cup_logo_copyrighted-128.png', #8 Java
            'Data/database-128.png', #9 DB
            'Data/grid-128.png', #10 excel
            'Data/mysql-128.png', #11 mysql
            'Folders/archive2-128.png', #12 archive
            'Operating_Systems/linux-128.png', #13 Linux
            'User_Interface/run_command-128.png', #14 command prompt
            'Security/key_security-128.png', #15 security
            'Computer_Hardware/cd-128.png', #16 cd, image files
            'Very_Basic/download-128.png', #17 download icon
            'Computer_Hardware/burn_cd-128.png', #18 iso, dmg, etc
            'Industry/trash-128.png', # 19, trash bin
            'Very_Basic/folder_back-128.png', # 20 folder move back
            'Very_Basic/folder-128.png' #21
            ]

        self.additional_icons_exts = {
            'srt': 0, 'nfo': 1, 'psd': 3, 'eps': 5, 'swf': 4, 'py': 7,
            'idx': 0, 'php': 6, 'aspx': 2, 'ai': 5, 'as': 4, 'pyc': 7,
            'smi': 0, 'html': 2, 'cfm': 2, 'ait': 5, 'asc': 4, 'java': 8,
            'ssa': 0, 'htm': 2, 'asp': 2, 'fla': 4, 'jsfl': 4,
            'accdb': 9, 'accdc': 9, 'nv2': 9, 'cdb': 9, 'accde': 9, 'alf': 9,
            'kexis': 9, 'dbc': 9, 'mdbhtml': 9, 'rod': 9, 'dbf': 9, 'accdr': 9,
            'dbx': 9, 'gdb': 9, 'accdw': 9, 'accdt': 9, 'itw': 9, 'dbs': 9,
            'dbt': 9, 'dbv': 9, 'rctd': 9, 'adp': 9, 'dqy': 9, 'adf': 9,
            'fic': 9, 'ade': 9, 'adb': 9, 'adn': 9, 'te': 9, 'itdb': 9,
            'dad': 9, 'mpd': 9, 'his': 9, 'xdb': 9, 'db': 9, 'p96': 9,
            'p97': 9, 'fol': 9, 'fmp12': 9, 'db3': 9, 'db2': 9, 'trm': 9,
            'vis': 9, 'trc': 9, 'xld': 9, 'dadiagrams': 9, 'cma': 9, 'pan': 9,
            'rpd': 9, 'mdn': 9, 'btr': 9, 'mdb': 9, 'mdf': 9, 'kdb': 15,
            'v12': 9, 'kexic': 9, 'odb': 9, 'accft': 9, 'mdt': 9, 'jtx': 9,
            'dsn': 9, 'mud': 9, 'abs': 9, 'tmd': 9, 'dsk': 9, 'ddl': 9,
            'abx': 9, 'fmpsl': 9, 'orx': 9, 'eco': 9, 'dcb': 9, 'sbf': 9,
            'dcx': 9, 'ask': 9, 'dct': 9, 'teacher': 9, 'ecx': 9, 'wdb': 9,
            'dp1': 9, 'gwi': 9, 'wmdb': 9, 'ndf': 9, 'pdm': 9, 'idb': 9,
            'marshal': 9, 'ihx': 9, 'sql': 9, 'nsf': 9, 'wrk': 9, 'kexi': 9,
            'qry': 9, 'daschema': 9, 'mwb': 9, 'fmp': 9, 'usr': 9,
            'ora': 9, 'pnz': 9, 'rsd': 9, 'lgc': 9, 'dtsx': 9, 'udb': 9,
            'vpd': 9, 'sdf': 9, 'sdb': 9, 'ns2': 9, 'ns3': 9, 'ns4': 9,
            'udl': 9, 'fdb': 9, 'dacpac': 9, 'fm5': 9, 'cat': 9, 'scx': 9,
            'hdb': 9, 'rbf': 9, 'sqlite': 9, 'maw': 9, 'spq': 9, 'oqy': 9,
            'dxl': 9, 'ib': 9, 'sis': 9, 'owc': 9, 'fpt': 9, 'pass': 15,
            'qvd': 9, 'sqlite3': 9, 'nyf': 9, 'nv': 9, 'maq': 9, 'mas': 9,
            'mar': 9, 'edb': 9, 'mav': 9, 'daconnections': 9, 'sqlitedb': 9, 'fcd': 9,
            'maf': 9, 'abcddb': 9, 'nrmlib': 9, 'db-shm': 9, 'cpd': 9, 'pdb': 9,
            'fp5': 9, 'fp4': 9, 'fp7': 9, 'tps': 9, 'ckp': 9, 'fp3': 9,
            'mrg': 9, 'db-wal': 9, 'xlsx': 10, 'xlsm': 10, 'xlsb': 10, 'xltx': 10,
            'xltm': 10, 'xls': 10, 'xlt': 10, 'xlam': 10, 'xla': 10, 'xlw': 10,
            'frm': 11, 'myd': 11, 'myi': 11, 'password': 15, 'nzb': 17, 'torrent': 17,
            'yz1': 12, 'uca': 12, 'zpaq': 12, 'pim': 12, 'lzx': 12, 'tgz': 12,
            'wim': 12, 'gz': 12, 'sitx': 12, 'apk': 12, 'arc': 12, 'alz': 12,
            'b1': 12, 'sea': 12, 'ucn': 12, 'sen': 12, 'arj': 12, 'partimg': 12,
            'pit': 12, 'cfs': 12, 'uc2': 12, 'gca': 12, 'ear': 12, 'zz': 12,
            'zip': 12, 'sit': 12, 'tar.z': 12, 'xar': 12, 'uc0': 12, 'jar': 12,
            'afa': 12, 'ice': 12, '7z': 12, 'zipx': 12, 'kgb': 12, 'ur2': 12,
            'pak': 12, 'pea': 12, 'rk': 12, 'dgc': 12, 'sqx': 12, 'ba': 12,
            'sfx': 12, 'qda': 12, 'dd': 12, 'bh': 12, 'lzh': 12, 'hki': 12,
            'paq6': 12, 'sda': 12, 'dar': 12, 'ha': 12, 'tar.bz2': 12, 'ue2': 12,
            'zoo': 12, 'ace': 12, 'tlz': 12, 'uha': 12, 'tar.lzma': 12,
            'war': 12, 'tar.gz': 12, 's7z': 12, 'tbz2': 12, 'xp3': 12, 'cab': 12,
            'rar': 12, 'cpt': 12, 'uc': 12, 'sh': 14, 'batch': 14, 'au3': 14, 'au2': 14,
            'au': 14, 'vbs': 14, 'magnet': 17, 'mdx': 16,
            'ibb': 16, 'ibq': 16, 'ibp': 16, 'bin': 16, 'cd': 16,
            'ccd': 16, 'p01': 16, 'isz': 16, 'hfv': 16, 'nfi': 16, 'cl5': 16,
            'hfs': 16, 'sdi': 16, 'avhd': 16, 'flp': 16, 'swm': 16, 'sqfs': 16,
            'fdi': 16, 'dvd': 16, 'd00': 16, 'd01': 16, 'disk': 16, 'vaporcd': 16,
            'disc': 16, 'ipf': 16, 'd88': 16, 'cdr': 16, 'cdt': 16, 'td0': 16,
            'cdi': 16, 'cso': 16, 'cdm': 16, 'bdf': 16, 'wlz': 16, 'sub': 16,
            'wmt': 16, 'gbi': 16, 'mds': 16, 'dvdr': 16, 'rcl': 16, 'sparsebundle': 16,
            'dbr': 16, 'x64': 16, 'xmf': 16, 'k3b': 16,
            'sopt': 16, 'ecm': 16, 'hdd': 16, 'gkh': 16, 'hdi': 16, 'hds': 16,
            'pdi': 16, 'xa': 16, 'bwi': 16, 'dms': 16, 'd64': 16, 'md2': 16,
            'md1': 16, 'md0': 16, 'bwa': 16, 'toast': 16, 'gcd': 16, 'bwz': 16,
            'cif': 16, 'ashdisc': 16, 'bws': 16, 'st': 16, 'bwt': 16,
            'p2g': 16, 'volarchive': 16, 'lnx': 16, 'ima': 16, '2mg': 16, 'vhdx': 16,
            'img': 16, 'imz': 16, 'sdsk': 16, 'qcow': 16, 'xdi': 16, 'tzx': 16,
            'i02': 16, 'i01': 16, 'i00': 16, 'fdd': 16, 'eui': 16,
            'edv': 16, 'b5i': 16, 'eds': 16, 'edq': 16, 'adz': 16,
            'edk': 16, 'b5t': 16, 'ede': 16, 'flg': 16, 'uibak': 16, 'eda': 16,
            'tib': 16, 't64': 16, 'udf': 16, 'pxi': 16, 'ndif': 16, 'sco': 16,
            'l01': 16, 'vmwarevm': 16, 'vc4': 16, 'vc6': 16, 'vc8': 16,
            'nn': 16, 'winclone': 16, 'image': 16, 'rdf': 16, 'bif': 16,
            'dcf': 16, 'vdi': 16, 'tap': 16, 'aa': 16, 'vcd': 16, 'xmd': 16,
            'mlc': 16, 'vco': 16, 'mbi': 16, 'wil': 16, 'simg': 16,
            'wii': 16, 'vcx': 16, 'c2d': 16, 'dmgpart': 16, 'xva': 16, 'afd': 16,
            'ixa': 16, 'aff': 16, 'toc': 16, 'tc': 16, 'afm': 16, 'uif': 16,
            'pvm': 16, 'mir': 16, 'daa': 16, 'ufs': 16, 'pgx': 16, 'dao': 16,
            'gdrive': 16, 'pgd': 16, 'dax': 16, 'qcow2': 16, 'e01': 16,
            'ratdvd': 16, 'b6i': 16, 'cue': 16, 'ncd': 16, 'vhd': 16, 'lcd': 16,
            'vfd': 16, 'p2i': 16, 'b6t': 16, 'dxp': 16, 'vmdk': 16,
            'omg': 16, 'atr': 16, 'g41': 16, 'gi': 16, '000': 16, 'sparseimage': 16,
            'pqi': 16, 'nri': 16, 'nrg': 16, 'tao': 16, 'mrimg': 16,
            'dmg': 18, 'iso': 18, 'tmp': 19, 'temp': 19
            }