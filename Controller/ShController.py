from typing import List
from Entity.Publics import NicknameSH

#Obtiene los alias del Sh  
def trainEntNicknamesSHByClientId(train_paterns:List[NicknameSH]):
    patterns = []

    for sh in train_paterns:
            nicknames = str(sh.alias).split(',')
            label = nicknames[0]

            for nickname in str(sh.alias).split(','):
                patterns.append({"label": label, "pattern": nickname})

    return patterns

#Obtiene el name_screen de tweeter
def trainEntNicknamesPrinSHByClientId(train_paterns:List[NicknameSH]):
    patterns = []

    for sh in train_paterns:
            nicknames = str(sh.alias).split(',')
            label = nicknames[0]
            patterns.append({"label": label})
    return patterns