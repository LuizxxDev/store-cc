import random
from card_generator import complete_card_info, generate_expiry, generate_cvv

# Dicionário de prefixos de BINs por tipo de cartão
BIN_PREFIXES = {
    "VISA": ["4539", "4556", "4916", "4532", "4929"],
    "MASTERCARD": ["51", "52", "53", "54", "55"],
    "AMEX": ["34", "37"],
}

# Função para gerar um BIN aleatório de acordo com o tipo de cartão
def generate_bin(card_type):
    if card_type not in BIN_PREFIXES:
        raise ValueError(f"Tipo de cartão desconhecido: {card_type}")
    
    prefix = random.choice(BIN_PREFIXES[card_type])  # Escolhe um prefixo aleatório
    return prefix

# Função para testar a geração de BINs e validação do cartão
def test_card_generation():
    card_types = ["VISA", "MASTERCARD", "AMEX"]
    
    for card_type in card_types:
        bin_prefix = generate_bin(card_type)  # Gera o BIN do cartão
        expiry_date = generate_expiry()  # Gera a data de expiração
        cvv = generate_cvv(card_type)  # Gera o CVV do cartão
        
        # Completa as informações do cartão
        card_info = complete_card_info(f"{bin_prefix}|{expiry_date}|{cvv}")
        
        # Exibe as informações geradas
        print(f"Testando {card_type} - BIN gerado: {bin_prefix}")
        print(f"Data de expiração gerada: {expiry_date}")
        print(f"CVV gerado: {cvv}")
        print(f"Informações completas do cartão: {card_info}")
        print("-" * 40)

# Chama a função de teste
if __name__ == "__main__":
    test_card_generation()
