from fuzzywuzzy import fuzz

# Strings de exemplo
string1 = "Python is awesome"
string2 = "Python is awesome"

# Calcular a porcentagem de similaridade
porcentagem = fuzz.ratio(string1, string2)

print(f"A porcentagem de similaridade entre as strings é: {porcentagem}%")
