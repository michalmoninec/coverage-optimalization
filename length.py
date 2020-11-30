while True:
    variable = input('Zadej promennou:')
    print('Delka je {}'.format(len(variable)))
    if len(variable) > 10:
        print('Musis opravit delku!')
