import mercadopago
import telebot
import time
import base64
import random

from io import BytesIO
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TELEGRAM_TOKEN, MERCADOPAGO_ACCESS_TOKEN
from card_generator import complete_card_info, generate_expiry, generate_cvv


# Inicializando o bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Inicializando Mercado Pago
mp = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

# Dicionário para armazenar informações dos usuários
user_data = {}

# Função para criar pagamento via Pix
def create_pix_payment(amount, user_id):
    payment_data = {
        "transaction_amount": amount,
        "description": "Compra de CC via Pix",
        "payment_method_id": "pix",
        "payer": {
            "email": f"user_{user_id}@example.com"
        }
    }
    
    payment_response = mp.payment().create(payment_data)

    if "response" in payment_response and "id" in payment_response["response"]:
        payment = payment_response["response"]
        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
        qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        payment_id = payment["id"]
        return qr_code, qr_code_base64, payment_id
    else:
        return None, None, None

# Função para verificar pagamento automaticamente
def check_payment_status(payment_id):
    payment_status = mp.payment().get(payment_id)
    if payment_status["status"] == 200:
        payment_data = payment_status["response"]
        return payment_data["status"] == "approved"
    return False

# Loop para verificar pagamento automaticamente
# Função para verificar o pagamento automaticamente
def check_payment_loop(chat_id, payment_id):
    for _ in range(10):  # Tenta por 10 iterações (~50 segundos)
        time.sleep(5)  # Espera 5 segundos entre as verificações
        if check_payment_status(payment_id):
            # Definir um BIN aleatório com base em tipos de cartões
            card_types = {
                "VISA": ["4539", "4556", "4916", "4532", "4929"],
                "MASTERCARD": ["51", "52", "53", "54", "55"],
                "AMEX": ["34", "37"],
            }
            
            # Escolhe um tipo de cartão aleatoriamente
            card_type = random.choice(["VISA", "MASTERCARD", "AMEX"])
            bin_prefix = random.choice(card_types[card_type])  # Gera um BIN aleatório do tipo escolhido

            # Completa as informações do cartão com o BIN gerado
            card = complete_card_info(f"{bin_prefix}|{generate_expiry()}|{generate_cvv(card_type)}")
            
            bot.send_message(chat_id, f"✅ Pagamento aprovado! Aqui está sua CC:\n\n{card}")
            return
    bot.send_message(chat_id, "⚠️ O pagamento ainda não foi confirmado. Tente novamente mais tarde.")


# Função para converter base64 em imagem
def base64_to_image(base64_string):
    image_data = base64.b64decode(base64_string)
    return BytesIO(image_data)

IMAGE_PATH = "assets/perfil-telegram.png"

# Comando de boas-vindas
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id  

    # Mensagem de boas-vindas formatada corretamente
    welcome_text = (
        "🔥 *BEM\\-VINDO AO CARDER KODAK* 🔥\n\n"
        "⚠️ *CUIDADO COM OS FALSOS ADMINS*\n\n"
        "❌ *Nenhum ADM chama no PV*\n"
        "❌ *Nenhuma venda é feita no PV, CC é só no BOT SEMPRE*\n\n"
        "⚠️ *CUIDADO COM OS GRUPOS FALSOS*\n"
        "✅ *GRUPO OFICIAL:* [Clique aqui](https://t.me/consultaskodak)\n"
    )

    # Enviar mensagem primeiro
    bot.send_message(chat_id, welcome_text, parse_mode="MarkdownV2", disable_web_page_preview=True)

    # Enviar imagem logo após a mensagem
    with open(IMAGE_PATH, "rb") as photo:
        sent_photo = bot.send_photo(chat_id, photo)  # Armazena a mensagem da foto para usar nos botões

    # Criando os botões de produtos
    button_cc = InlineKeyboardButton("💳 COMPRAR CC", callback_data="buy_cc")
    profile_button = InlineKeyboardButton("👤 MINHA CONTA", callback_data="show_profile")
    button_saldo = InlineKeyboardButton("👑 DONO", callback_data="show_dono_info")

    # Adiciona os botões ao teclado
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button_cc)
    keyboard.add(button_saldo, profile_button)

    # Envia os botões logo abaixo da imagem
    bot.send_message(chat_id,"Por favor, escolha uma opção abaixo:", reply_markup=keyboard)

    # Exibe as informações do dono quando o botão DONO é pressionado
@bot.callback_query_handler(func=lambda call: call.data == "show_dono_info")
def show_dono_info(call):
    dono_info = (
        " *👑 DONO:*\n\n"
        "👤@kodakzx\n\n"
        "📍 GRUPO REF: [Clique aqui para entrar](https://t.me/consultaskodak)\n\n"
    )
    
    # Envia as informações do dono
    bot.send_message(
        call.message.chat.id,
        dono_info,
        parse_mode="MarkdownV2"
    )


# Envio de mensagem com aviso e tabela de preços
@bot.callback_query_handler(func=lambda call: call.data == "buy_cc")
def send_buy_cc(call):
    # Adicionando o texto antes das opções de compra
    buycc_text = (
        "💳 Comprar CC\n\n"
        "⚠️ Compre apenas se você estiver de acordo com as regras:\n\n"
        "NÃO GARANTIMOS SOMENTE LIVE!\n"
        "NÃO GARANTIMOS A APROVAÇÃO\n"
        "NÃO GARANTIMOS SALDO\n\n"
        "- Escolha abaixo o produto que deseja comprar.\n\n"
        "*TABELA DE PREÇOS:*\n\n"
        "| 💳 GOLD                      | R$25,00 |\n"
        "| 💳 MICRO BUSINESS             | R$48,00 |\n"
        "| 💳 NUBANK GOLD                | R$7,00  |\n"
        "| 💳 PREPAID BUSINESS           | R$32,00 |\n"
        "| 💳 PREPAID CLASSIC            | R$32,00 |\n"
        "| 💳 STANDARD                   | R$24,00 |\n"
        "| 💳 TRADITIONAL                | R$32,00 |\n"
        "| 💳 UATP                       | R$32,00 |\n"
    )

    # Escapando todos os caracteres especiais do Telegram, incluindo o '|'
    special_chars = ["!", "-", ".", "_", "*", "(", ")", "[", "]", "~", "`", "|"]
    for char in special_chars:
        buycc_text = buycc_text.replace(char, "\\" + char)

    # Adicionando os novos produtos
    keyboard = InlineKeyboardMarkup()
    cc_button_25 = InlineKeyboardButton("💳 GOLD - R$25", callback_data="buy_cc_25")
    cc_button_48 = InlineKeyboardButton("💳 MICRO BUSINESS - R$48", callback_data="buy_cc_48")
    cc_button_7 = InlineKeyboardButton("💳 NUBANK GOLD - R$7", callback_data="buy_cc_7")
    cc_button_32 = InlineKeyboardButton("💳 PREPAID BUSINESS - R$32", callback_data="buy_cc_32")
    cc_button_32_2 = InlineKeyboardButton("💳 PREPAID CLASSIC - R$32", callback_data="buy_cc_32_2")
    cc_button_24 = InlineKeyboardButton("💳 STANDARD - R$24", callback_data="buy_cc_24")
    cc_button_32_3 = InlineKeyboardButton("💳 TRADITIONAL - R$32", callback_data="buy_cc_32_3")
    cc_button_uatp = InlineKeyboardButton("💳 UATP - R$32", callback_data="buy_cc_uatp")
    back_button = InlineKeyboardButton("🔙 VOLTAR", callback_data="back_to_main")

    # Organizando os botões de 2 em 2
    keyboard.add(cc_button_25, cc_button_48)
    keyboard.add(cc_button_7, cc_button_32)
    keyboard.add(cc_button_32_2, cc_button_24)
    keyboard.add(cc_button_32_3, cc_button_uatp)
    keyboard.add(back_button)

    # Envia a mensagem com o texto e os botões
    bot.send_message(
        call.message.chat.id, 
        buycc_text,  # Texto com caracteres escapados
        parse_mode="MarkdownV2", 
        reply_markup=keyboard
    )


# Processamento de pagamento
# Processamento de pagamento
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_cc_"))
def handle_payment(call):
    amount_mapping = {
        "buy_cc_25": 00.01,
        "buy_cc_48": 48.00,
        "buy_cc_7": 7.00,
        "buy_cc_32": 32.00,
        "buy_cc_24": 24.00,
        "buy_cc_32_2": 32.00,
        "buy_cc_uatp": 32.00,
    }

    amount = amount_mapping.get(call.data)
    
    if not amount:
        return

    qr_code, qr_code_base64, payment_id = create_pix_payment(amount, call.from_user.id)

    # Criação do teclado de cancelamento
    keyboard = InlineKeyboardMarkup()
   

    if qr_code:
        user_data[call.message.chat.id] = {'payment_id': payment_id}

        # Envia o QR Code com o preço incluído na mensagem
        image = base64_to_image(qr_code_base64)
        bot.send_photo(call.message.chat.id, photo=image, caption=f"📸 Escaneie o QR Code para pagar. \nPreço: R${amount:.2f}")

        # Envia o código Pix Copia e Cola com o preço
        bot.send_message(call.message.chat.id, f"🔗 **Pix Copia e Cola:**\n\n`{qr_code}`")

        # Inicia a verificação automática do pagamento
        check_payment_loop(call.message.chat.id, payment_id)

    else:
        bot.send_message(call.message.chat.id, "❌ Erro ao gerar pagamento. Tente novamente mais tarde.")



# Função para voltar ao menu principal
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    # Passar o objeto message, não só o chat_id
    send_welcome(call.message)

# Inicia o bot
bot.polling()
