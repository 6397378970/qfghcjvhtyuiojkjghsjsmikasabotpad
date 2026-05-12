import requests
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = "8674194296:AAGqxTPggfH52IyefdVP8565SFOJcmspOwI"  # Replace with your bot token from @BotFather
API_URL = "https://api.ai4chat.co/v1/chat"  # Replace with actual API endpoint

# User session storage (in production, use a database)
user_sessions = {}

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        
        # Message handler for text
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Initialize user session
        user_sessions[user_id] = {
            'conversation_history': [],
            'last_active': datetime.now()
        }
        
        welcome_message = f"""
🎉 *Welcome, {user.first_name}!* 🎉

I'm your mikasa. I can help you with:

✍️ *Content Creation*
• Blog posts and articles
• Social media content
• Product descriptions
• Email newsletters

💡 *Creative Writing*
• Story ideas and outlines
• Poetry and creative pieces
• Character development
• Dialogue writing

📊 *Business Content*
• Marketing copy
• Sales scripts
• Business proposals
• SEO content

🎨 *Brainstorming*
• Campaign ideas
• Project concepts
• Problem solutions
• Creative strategies

*How to use:*
Simply type your request, and I'll help you create amazing content!

*Quick Examples:*
• "Write a product description for a smart watch"
• "Create a blog outline about AI technology"
• "Brainstorm marketing ideas for a coffee shop"

Use /menu to see all available options or just start chatting!
        """
        
        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("📝 create content", callback_data="create_content"),
             InlineKeyboardButton("💡 Get Ideas", callback_data="get_ideas")],
            [InlineKeyboardButton("❓ Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("🗑️ Clear Chat", callback_data="clear")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*🤖  Chatbot Help Guide*

*Basic Commands:*
/start - Start the bot
/help - Show this help message
/about - About this bot
/clear - Clear conversation history
/menu - Show menu options

*How to use:*
Just type your request naturally! For example:

• *Content Creation:*
  "Write a blog post about fitness tips"
  "Create a product description for headphones"

• *Brainstorming:*
  "Give me 10 ideas for YouTube videos"
  "Brainstorm marketing strategies for a bakery"

• *Writing:*
  "Write a short story about a robot"
  "Create an email for a sale promotion"

*Tips for best results:*
1. Be specific about your request
2. Mention your target audience
3. Specify the tone (professional, casual, funny)
4. Include any key points you want covered

*Example of a good request:*
"Write a professional product description for a wireless mouse targeting business professionals. Focus on productivity and comfort."

Need something specific? Just ask! 🚀
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        about_text = """
*ℹ️ About This Bot*

*Name:* 𝜧𝜾𝜿𝛼𝜹𝛼
*Creator:* Light
*Service:* AI4Chat
*Version:* 1.0.0

*Features:*
✅ AI-powered responses
✅ Content creation
✅ Idea generation
✅ Writing assistance
✅ 24/7 availability

*Technology:*
This bot uses advanced AI to understand your requests and generate high-quality content tailored to your needs.

*Status:* Active ✅
*API Status:* Connected

For support or feedback, contact @prexzy

*Rate Limit:* 50 requests per minute
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            about_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        if user_id in user_sessions:
            user_sessions[user_id]['conversation_history'] = []
            await update.message.reply_text(
                "✅ Conversation history cleared! We can start fresh now."
            )
        else:
            await update.message.reply_text(
                "No conversation history found. Just start chatting!"
            )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        keyboard = [
            [InlineKeyboardButton("📝 Content Creation", callback_data="create_content"),
             InlineKeyboardButton("💡 Idea Generation", callback_data="get_ideas")],
            [InlineKeyboardButton("✍️ Writing Help", callback_data="writing_help"),
             InlineKeyboardButton("🎨 Brainstorming", callback_data="brainstorm")],
            [InlineKeyboardButton("📊 Marketing Copy", callback_data="marketing"),
             InlineKeyboardButton("❓ Help & Support", callback_data="help")],
            [InlineKeyboardButton("🗑️ Clear Chat", callback_data="clear")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 *Main Menu*\n\nChoose an option below:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "create_content":
            await query.edit_message_text(
                "📝 *Content Creation Mode*\n\n"
                "What would you like me to create?\n\n"
                "Examples:\n"
                "• Blog post about [topic]\n"
                "• Product description for [product]\n"
                "• Social media post for [brand]\n"
                "• Email newsletter about [subject]\n\n"
                "Just type your request!",
                parse_mode='Markdown'
            )
        
        elif query.data == "get_ideas":
            await query.edit_message_text(
                "💡 *Idea Generation Mode*\n\n"
                "What kind of ideas do you need?\n\n"
                "Examples:\n"
                "• 10 business ideas for [industry]\n"
                "• Content ideas for [niche]\n"
                "• Marketing campaign ideas\n"
                "• YouTube video ideas about [topic]\n\n"
                "Tell me what you need ideas for!",
                parse_mode='Markdown'
            )
        
        elif query.data == "writing_help":
            await query.edit_message_text(
                "✍️ *Writing Help Mode*\n\n"
                "I can help you with:\n"
                "• Proofreading\n"
                "• Rewriting content\n"
                "• Expanding text\n"
                "• Summarizing\n"
                "• Improving tone\n\n"
                "Share your text and what you need help with!",
                parse_mode='Markdown'
            )
        
        elif query.data == "brainstorm":
            await query.edit_message_text(
                "🎨 *Brainstorming Mode*\n\n"
                "Let's brainstorm together! Share your topic:\n\n"
                "Examples:\n"
                "• Brainstorm names for a [type of business]\n"
                "• Creative solutions for [problem]\n"
                "• Slogans for [brand]\n"
                "• Features for [product]",
                parse_mode='Markdown'
            )
        
        elif query.data == "marketing":
            await query.edit_message_text(
                "📊 *Marketing Copy Mode*\n\n"
                "I can create marketing content like:\n"
                "• Sales copy\n"
                "• Ad scripts\n"
                "• Landing page content\n"
                "• Email campaigns\n"
                "• Social media ads\n\n"
                "Tell me about your product/service!",
                parse_mode='Markdown'
            )
        
        elif query.data == "help":
            help_text = """
*Quick Commands:*
/start - Restart bot
/help - Show help
/clear - Clear history
/menu - Show menu

*Tips:*
• Be specific with your requests
• Mention target audience
• Specify desired tone
• Ask for variations
            """
            await query.edit_message_text(help_text, parse_mode='Markdown')
            await self.menu_command(update, context)
        
        elif query.data == "about":
            await query.edit_message_text(
                "🤖 *AI Chatbot v1.0*\n"
                f"*Creator:* prexzy\n"
                f"*Service:* AI4Chat\n"
                f"*Status:* Active ✅\n\n"
                "Powered by advanced AI technology",
                parse_mode='Markdown'
            )
        
        elif query.data == "clear":
            user_id = update.effective_user.id
            if user_id in user_sessions:
                user_sessions[user_id]['conversation_history'] = []
                await query.edit_message_text("✅ Chat history cleared!")
            else:
                await query.edit_message_text("No history to clear!")
        
        elif query.data == "menu":
            await self.menu_command(update, context)
    
    async def call_ai_api(self, user_message: str, user_id: int) -> str:
        """Call the AI API to get response"""
        try:
            # Get conversation history
            history = user_sessions.get(user_id, {}).get('conversation_history', [])
            
            # Prepare request payload according to your API format
            payload = {
                "message": user_message,
                "service": "AI4Chat",
                "history": history[-10:] if history else [],  # Send last 10 messages for context
                "creator": "prexzy"
            }
            
            # Make API request
            response = requests.post(
                API_URL,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Parse response according to your API format
                if data.get('status') and data.get('data', {}).get('response'):
                    bot_response = data['data']['response']
                elif data.get('response'):
                    bot_response = data['response']
                else:
                    bot_response = "I received your message but couldn't generate a proper response. Could you rephrase?"
                
                # Store in history
                if user_id in user_sessions:
                    user_sessions[user_id]['conversation_history'].append({
                        'user': user_message,
                        'bot': bot_response,
                        'timestamp': datetime.now().isoformat()
                    })
                
                return bot_response
            
            else:
                logger.error(f"API Error: {response.status_code}")
                return self.get_fallback_response(user_message)
                
        except requests.exceptions.Timeout:
            logger.error("API Timeout")
            return "Sorry, the AI service is taking too long. Please try again in a moment."
        
        except requests.exceptions.ConnectionError:
            logger.error("API Connection Error")
            return "Unable to connect to AI service. Please check your internet connection."
        
        except Exception as e:
            logger.error(f"API Exception: {str(e)}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, message: str) -> str:
        """Fallback responses when API is unavailable"""
        responses = {
            'hi': "👋 Hello! How can I help you create something amazing today?",
            'hello': "Hey there! Ready to create some awesome content? What's on your mind?",
            'how are you': "I'm functioning perfectly! Ready to help you with your creative projects. What would you like to create?",
            'help': "I can help you create content, generate ideas, write copy, brainstorm solutions, and much more! Just tell me what you need.",
            'create': "Great! Let's create something together. Tell me:\n\n1. What type of content?\n2. Who is your audience?\n3. What tone do you prefer?\n4. Any specific requirements?"
        }
        
        lower_msg = message.lower()
        for key, response in responses.items():
            if key in lower_msg:
                return response
        
        return f"""Thanks for your message! I'm here to help you create amazing content.

Based on: "{message[:50]}..."

To get the best results, please tell me:
• What type of content you need (blog, description, email, etc.)
• Your target audience
• Preferred tone (professional, casual, funny, serious)
• Any key points to include

Or just describe what you want to create! 🚀"""
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_message = update.message.text
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get AI response
            bot_response = await self.call_ai_api(user_message, user_id)
            
            # Split long messages (Telegram limit is 4096 characters)
            if len(bot_response) > 4000:
                for i in range(0, len(bot_response), 4000):
                    await update.message.reply_text(bot_response[i:i+4000])
            else:
                await update.message.reply_text(bot_response)
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text(
                "Sorry, I encountered an error. Please try again or use /start to reset the bot."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "An error occurred. Please try again later or use /start to restart the bot."
                )
        except:
            pass
    
    def run(self):
        """Run the bot"""
        self.setup_handlers()
        logger.info("Bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ WARNING: Please replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token!")
        print("Get your token from @BotFather on Telegram")
        return
    
    try:
        bot = TelegramBot(BOT_TOKEN)
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")

if __name__ == '__main__':
    main()
