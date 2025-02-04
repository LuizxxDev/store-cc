import random

# Função para verificar o tipo do cartão com base no prefixo (BIN)
def detect_card_type(prefix):
    visa_prefix = ["4539", "4556", "4916", "4532", "4929", "40240071", "4485", "4716"]
    mastercard_prefix = ["51", "52", "53", "54", "55"]
    amex_prefix = ["34", "37"]

    if any(prefix.startswith(v) for v in visa_prefix):
        return "VISA"
    elif any(prefix.startswith(m) for m in mastercard_prefix):
        return "MASTERCARD"
    elif any(prefix.startswith(a) for a in amex_prefix):
        return "AMEX"
    else:
        return "DESCONHECIDO"

# Algoritmo de Luhn para gerar o número do cartão
def luhn_algorithm(prefix, length):
    number = [int(digit) for digit in prefix]
    
    # Preenche os dígitos faltantes, se necessário, sem sobrescrever
    while len(number) < length - 1:
        number.append(random.randint(0, 9))

    # Calcula o dígito de verificação (último dígito)
    total = sum(number[-2::-2]) + sum(sum(divmod(2 * d, 10)) for d in number[-1::-2])
    check_digit = (10 - (total % 10)) % 10
    number.append(check_digit)
    
    return "".join(map(str, number))

# Função para gerar um número de cartão de crédito com um prefixo específico
def generate_credit_card_number(prefix, length=16):
    # Garante que o número gerado seja completado corretamente, sem sobrescrever
    return luhn_algorithm(prefix, length)

# Função para gerar uma data de expiração (mês/ano)
def generate_expiry():
    return f"{random.randint(1, 12):02d}|{random.randint(2025, 2030)}"

# Função para gerar o CVV (3 ou 4 dígitos, dependendo do tipo de cartão)
def generate_cvv(card_type):
    if card_type != "AMEX":
        return f"{random.randint(100, 999)}"
    else:
        return f"{random.randint(1000, 9999)}"

# Função que completa as informações do cartão de crédito
def complete_card_info(user_input):
    data = user_input.split("|")

    bin_prefix = data[0]  # Usa o BIN completo como prefixo
    card_type = detect_card_type(bin_prefix)  # Detecta o tipo do cartão

    # Gera o número do cartão, caso o usuário não tenha informado
    card_number = generate_credit_card_number(bin_prefix)

    # Gera a data de validade e CVV caso o usuário não tenha informado
    expiry = data[1] if len(data) > 1 else generate_expiry()
    cvv = data[2] if len(data) > 2 else generate_cvv(card_type)

    return f"{card_number}|{expiry}|{cvv}  TIPO: {card_type}"
