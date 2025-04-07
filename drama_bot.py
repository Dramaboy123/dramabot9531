import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import asyncio
import io
import os
import sys
import platform
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Placeholder for your prediction model and logic
async def predict_candles(image_or_history):
    """
    Placeholder function to simulate candle prediction.
    Replace this with your actual prediction logic.

    Args:
        image_or_history: Either an image (from a screenshot) or historical data.

    Returns:
        A dictionary containing the prediction results.
    """
    await asyncio.sleep(1)  # Simulate processing time

    # Prototype logic: Randomly generate predictions
    predictions = {}
    intervals = ["1min", "5min", "30min"]
    for interval in intervals:
        prediction_options = ["UP", "DOWN", "NO TRADE"]
        prediction = random.choice(prediction_options)
        confidence = random.uniform(0.6, 1.0) if prediction != "NO TRADE" else random.uniform(0.1, 0.4)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        candle_time = f"{hour:02d}:{minute:02d}"
        predictions[interval] = {
            "prediction": prediction,
            "confidence": confidence,
            "candle_time": candle_time,
        }
    return predictions



# Placeholder for chart generation
async def generate_chart(predictions):
    """
    Placeholder function to generate a mini chart image.
    Replace this with your actual chart generation code.

    Args:
        predictions: The prediction data (dictionary).

    Returns:
        A byte stream of the chart image (PNG, JPG, etc.).
        Returns None if chart generation fails.
    """
    await asyncio.sleep(0.5)
    img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x06\x00\x00\x00\x11\x15\xe9\x82\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfc\x05\xea\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x1dIDATx\xda\x03\x01\x01\x00\x00\x00\x00K\xbc\xfc\xff\x03\x00\x01_\x00\x05\x02\xfd\x07\x04\x08\x04\x00\x00\x00\x00IEND\xaeB`\x82"
    return io.BytesIO(img)



# Define a global variable for the bot
bot = None


# Telegram bot handler functions
async def start(update, context):
    """Sends a welcome message to the user."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the Candle Prediction Bot! Send me a screenshot or historical data, and I'll predict the next candles.",
    )



async def handle_message(update, context):
    """Handles messages from the user, including images (screenshots)
    and text (which might represent historical data).
    """
    chat_id = update.effective_chat.id
    global bot

    if update.message.photo:
        # User sent a photo (screenshot)
        photo = update.message.photo[-1]
        try:
            file_id = photo.file_id
            file = await bot.get_file(file_id)
            file_bytes = await file.download_as_bytearray()
            image_bytes = bytes(file_bytes)
        except Exception as e:
            logger.error(f"Error downloading photo: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error downloading the image. Please try again.",
            )
            return

        await context.bot.send_message(chat_id=chat_id, text="Analyzing screenshot...")
        try:
            predictions = await predict_candles(image_bytes)
            await send_predictions(context.bot, chat_id, predictions)
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing the image. Please try again.",
            )

    elif update.message.text:
        # User sent text (assume it's historical data)
        historical_data = update.message.text
        await context.bot.send_message(chat_id=chat_id, text="Analyzing historical data...")
        try:
            predictions = await predict_candles(historical_data)
            await send_predictions(context.bot, chat_id, predictions)
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing the data. Please try again.",
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="I can't understand that. Please send a screenshot or historical data.",
        )



async def send_predictions(bot, chat_id, predictions):
    """Sends the predictions and chart to the user."""

    message_text = "Here are the candle predictions:\n"
    for interval, data in predictions.items():
        message_text += f"\n{interval}:\n"
        message_text += f"  Time: {data['candle_time']}\n"
        message_text += f"  Prediction: {data['prediction']}\n"
        message_text += f"  Confidence: {data['confidence']:.2f}\n"

    await bot.send_message(chat_id=chat_id, text=message_text)

    # Generate and send the chart
    try:
        chart_image = await generate_chart(predictions)
        if chart_image:
            await bot.send_photo(
                chat_id=chat_id, photo=chart_image, caption="Mini Chart Preview"
            )
        else:
            await bot.send_message(
                chat_id=chat_id, text="Failed to generate chart."
            )
    except Exception as e:
        logger.error(f"Error generating/sending chart: {e}")
        await bot.send_message(
                chat_id=chat_id, text="Failed to generate chart."
            )



async def error_handler(update, context):
    """Handles errors that occur in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="An error occurred. Please try again.",
    )



async def main():
    """Main function to start the bot."""
    global bot
    # Load your bot token from the environment variable.
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        logging.critical("BOT_TOKEN environment variable is not set!")
        sys.exit(1)

    # Create the Telegram Bot object.  Use the global 'bot'
    bot = telegram.Bot(token=bot_token)

    # Create the Updater and pass it your bot's token.
    updater = Updater(bot=bot, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.all, handle_message))

    # Register the error handler
    dispatcher.add_error_handler(error_handler)
    webhook_url = os.environ.get("WEBHOOK_URL")
    port = int(os.environ.get("PORT", "8080"))

    if webhook_url:
        try:
            await updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=bot_token,
                webhook_url=f"{webhook_url}/{bot_token}",
            )
            await bot.set_webhook(url=f"{webhook_url}/{bot_token}")
            logger.info(f"Webhook set to {webhook_url}/{bot_token}")
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            sys.exit(1)
    else:
        logger.info("Starting bot with long polling")
        updater.start_polling()


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.
    updater.idle()



if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
