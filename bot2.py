import telebot
import mercadopago

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TELEGRAM_TOKEN
from card_generator import complete_card_info

bot = telebot.TeleBot(TELEGRAM_TOKEN)

mp = mercadopago.MP("CLIENT_ID", "CLIENT_SECRET")

# Função para validar a quantidade de cartões
def validate_quantity(quantity):
    try:
        quantity = int(quantity)
        if quantity <= 10:
            return quantity
        else:
            return None
    except ValueError:
        return None

# Função para controlar o estado da conversa com o usuário
user_data = {}

# Função para gerar um pagamento via Pix
def create_pix_payment(amount):
    payment_data = {
        "transaction_amount": amount,
        "description": "Compra de CC via Pix",
        "payment_method_id": "pix",
        "payer": {
            "email": "test_user@test.com"  # Substitua pelo email do comprador
        }
    }
    # Criar o pagamento
    payment_response = mp.payment.create(payment_data)
    if payment_response["status"] == 201:  # Se o pagamento foi criado com sucesso
        payment = payment_response["response"]
        qr_code_url = payment["point_of_interaction"]["transaction_data"]["qr_code"]  # URL do QR Code do Pix
        payment_id = payment["id"]
        return qr_code_url, payment_id
    else:
        return None, None

# Comando de boas-vindas
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Este bot foi criado para gerar cc de maneira rápida e fácil. "
        "Com ele, você pode gerar cc, juntamente com dados como a data de validade e o CVV. 💳 "
    )

    # Criando um botão de "Mostrar Perfil"
    button_cc = InlineKeyboardButton("💳 COMPRAR CC", callback_data="buy_cc")
    profile_button = InlineKeyboardButton("👤 MINHA CONTA", callback_data="show_profile")
    button_saldo = InlineKeyboardButton("💰 ADICIONAR SALDO", callback_data="add_balance")

    # Adiciona os botões ao teclado
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button_cc)
    keyboard.add(button_saldo, profile_button)

    # Envia a mensagem com os botões
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_profile")
def show_profile(call):
    user = call.from_user  # Acessa as informações do usuário que chamou a função
    
    # Criando uma resposta com as informações do perfil do usuário
    profile_info = f"""
    📛 Nome: {user.first_name} {user.last_name if user.last_name else ''}
    🆔 ID de usuário: {user.id}
    💬 Nome de usuário: @{user.username if user.username else 'Não definido'}
    🌍 Idioma: {user.language_code}
    """
    # Envia as informações do perfil
    bot.send_message(call.message.chat.id, profile_info)


# Função de "Comprar CC"
@bot.callback_query_handler(func=lambda call: call.data == "buy_cc")
def send_buy_cc(call):
    buycc_text = (
        "COMPRAR CC 💳\n"
        "ESCOLHA ABAIXO O PRODUTO QUE DESEJA"
    )

    # Criação do teclado com o botão de comprar
    keyboard = InlineKeyboardMarkup()
    cc_button = InlineKeyboardButton("💳 CC - R$10", callback_data="buy_cc_10")
    back_button = InlineKeyboardButton("🔙 VOLTAR", callback_data="start")

    keyboard.add(cc_button)
    keyboard.add(back_button)

    # Envia a mensagem com os botões
    bot.send_message(
        call.message.chat.id, 
        buycc_text, 
        reply_markup=keyboard
    )

    # Quando o usuário escolhe o produto "CC - R$10"
@bot.callback_query_handler(func=lambda call: call.data == "buy_cc_10")
def handle_payment(call):
    amount = 10.00  # Valor do CC
    qr_code_url, payment_id = create_pix_payment(amount)

    if qr_code_url:
        # Salva o ID do pagamento para acompanhamento
        user_data[call.message.chat.id] = {'payment_id': payment_id}
        
        # Envia o QR Code para o usuário
        bot.send_message(call.message.chat.id, f"Para realizar o pagamento, escaneie o QR Code abaixo ou copie o código PIX.")
        bot.send_photo(call.message.chat.id, qr_code_url)
        bot.send_message(call.message.chat.id, "Aguarde até que o pagamento seja confirmado para gerar seu CC.")
    else:
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao gerar o pagamento. Tente novamente mais tarde.")

# Verifica o status do pagamento
def check_payment_status(payment_id):
    payment_status = mp.payment.get(payment_id)
    if payment_status["status"] == 200:
        payment_data = payment_status["response"]
        if payment_data["status"] == "approved":
            return True  # Pagamento aprovado
        else:
            return False  # Pagamento não aprovado
    return False  # Erro na verificação

# Comando para iniciar o processo de geração de cartões
@bot.message_handler(commands=['gen'])
def ask_for_bin(message):
    user_input = message.text.strip().split()

    bin_prefix = user_input[1]
    user_data[message.chat.id] = {'card_data': bin_prefix}
    
    # Pergunta quantos cartões o usuário quer gerar usando botões com emojis
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("1️⃣", callback_data="1")
    button2 = InlineKeyboardButton("2️⃣", callback_data="2")
    button3 = InlineKeyboardButton("3️⃣", callback_data="3")
    button4 = InlineKeyboardButton("4️⃣", callback_data="4")
    button5 = InlineKeyboardButton("5️⃣", callback_data="5")
    button6 = InlineKeyboardButton("6️⃣", callback_data="6")
    button7 = InlineKeyboardButton("7️⃣", callback_data="7")
    button8 = InlineKeyboardButton("8️⃣", callback_data="8")
    button9 = InlineKeyboardButton("9️⃣", callback_data="9")
    button10 = InlineKeyboardButton("🔟", callback_data="10")

    keyboard.add(button1, button2, button3, button4, button5,button6,button7,button8,button9, button10)
    
    bot.reply_to(message, f"Você enviou o BIN: {bin_prefix}. Quantos cartões você deseja gerar?", reply_markup=keyboard)

# Quando o usuário escolhe a quantidade de cartões
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_card_data = user_data.get(call.message.chat.id, {}).get('card_data', None)

    # Captura a quantidade de cartões escolhida
    quantity = int(call.data)

    # Gera os cartões solicitados
    cards = [complete_card_info(user_card_data) for _ in range(quantity)]
    response = "\n\n".join(cards)
    bot.send_message(call.message.chat.id, response)
    bot.answer_callback_query(call.id)

    # Função para processar quando o pagamento for confirmado
@bot.message_handler(commands=['verify_payment'])
def verify_payment(message):
    user_payment_id = user_data.get(message.chat.id, {}).get('payment_id', None)
    
    if not user_payment_id:
        bot.reply_to(message, "Você ainda não iniciou um pagamento.")
        return

    payment_status = check_payment_status(user_payment_id)

# Inicia o bot para ouvir as mensagens
bot.polling()
