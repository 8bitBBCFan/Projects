
s = 'Elektor120_2017-6-Nov :  14 [7]  34 [3]  37 [6] '

# get page number dependent on xpos
def get_page(xpos, s):
    def __scan(dr):
        i = 0
        while s[xpos+i].isdigit(): i += dr
        return (xpos+i+1 if i!=0 and s[xpos+i]==' ' else -1)

    if xpos<len(s) and s!='':
        i_left, i_right = __scan(-1), __scan(+1)
        if i_left!=-1 and i_right!=-1:
            return int(s[i_left:i_right])
    return(-1)

print(get_page(27, s))
