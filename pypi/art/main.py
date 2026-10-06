from art import art, artError

art_1 = art("coffee")
print("1. Cafe:\n", art_1)

art_2 = art("woman", number=2)
print("\n2. Repetido:\n", art_2)

art_3 = art("coffee", number=3, space=5)
print("\n3. Com espacos:\n", art_3)

print("\n4. Aleatorio:\n", art("random"))

# Tratando o erro ao passar um número em vez de string
try:
    art(22, number=1)
except artError as e:
    print("\n5. Erro capturado com sucesso:", e)