import os
import asyncio
import json
import sqlite3
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from runtime.executor import execute_workflow
from database import DB_PATH

class TelegramBot:
    def __init__(self):
        # Don't read env here, read it in run() to ensure dotenv is loaded
        self.token = None
        self.active_user_workflows = {} # user_id -> workflow_id

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "⚡ *Welcome to AgentFlow!* \n\n"
            "I am your autonomous agent portal. I can trigger complex multi-agent workflows directly from here.\n\n"
            "Use /workflows to see what I can do.",
            parse_mode='Markdown'
        )

    async def list_workflows(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("DEBUG: Fetching workflows for Telegram...")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        workflows = conn.execute("SELECT id, name FROM workflows").fetchall()
        conn.close()
        
        print(f"DEBUG: Found {len(workflows)} workflows.")

        if not workflows:
            await update.message.reply_text("No workflows configured yet. Create some in the AgentFlow dashboard first!")
            return

        keyboard = []
        for wf in workflows:
            keyboard.append([InlineKeyboardButton(wf['name'], callback_data=f"wf_{wf['id']}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a workflow to trigger:", reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        wf_id = query.data.replace("wf_", "")
        user_id = query.from_user.id
        self.active_user_workflows[user_id] = wf_id
        
        await query.edit_message_text(text="Great! Now send me the input prompt or topic for this workflow:")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if user_id not in self.active_user_workflows:
            await update.message.reply_text("Please select a workflow first using /workflows")
            return

        wf_id = self.active_user_workflows.pop(user_id)
        prompt = update.message.text
        
        status_msg = await update.message.reply_text("⚙️ *Orchestrating agents...*", parse_mode='Markdown')
        
        try:
            # Trigger our existing execution engine
            result = await execute_workflow(wf_id, prompt, trigger_source="telegram")
            final_output = result.get("result", "Execution finished but no result was returned.")
            
            # 1. Handle local images
            import re
            img_match = re.search(r'!\[.*?\]\((/static/generated_images/.*?)\)', final_output)
            if img_match:
                img_path = img_match.group(1)
                full_img_path = os.path.join(os.getcwd(), img_path.lstrip('/'))
                if os.path.exists(full_img_path):
                    try:
                        await update.message.reply_photo(photo=open(full_img_path, 'rb'), caption="🎨 Generated Result")
                    except Exception as e:
                        print(f"Error sending photo: {e}")
                final_output = re.sub(r'!\[.*?\]\(/static/generated_images/.*?\)', '', final_output)

            # 2. Final Report Delivery - USE HTML for better reliability
            # Cleanup for HTML mode
            import html
            safe_output = html.escape(final_output)
            # Restore basic formatting
            safe_output = safe_output.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            
            if len(safe_output) > 4000:
                safe_output = safe_output[:3900] + "\n\n<b>(Output truncated)</b>"

            try:
                await status_msg.edit_text(f"✅ <b>Workflow Complete</b>\n\n{final_output}", parse_mode='HTML')
            except Exception as e:
                # If HTML fails, send as plain text
                await status_msg.edit_text(f"✅ Workflow Complete:\n\n{final_output[:3900]}")

        except Exception as e:
            await status_msg.edit_text(f"❌ *Execution Failed*\nError: {str(e)}")

    async def run(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token or "your_telegram" in self.token or not self.token.strip():
            print("❌ TELEGRAM ERROR: Token not set or invalid in .env")
            return

        # Explicitly wait to allow old instances to die
        await asyncio.sleep(1)

        # Force clear any existing webhook/polling session
        try:
            import requests
            requests.get(f'https://api.telegram.org/bot{self.token}/deleteWebhook?drop_pending_updates=True', timeout=5)
        except: 
            pass

        print(f"📡 Initializing Telegram Bot: {self.token[:10]}...")
        
        try:
            # Build application with custom timeouts to handle high tool usage latency
            app = ApplicationBuilder().token(self.token).read_timeout(60).connect_timeout(60).build()
            
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CommandHandler("workflows", self.list_workflows))
            app.add_handler(CommandHandler("workflow", self.list_workflows))
            app.add_handler(CallbackQueryHandler(self.handle_callback))
            app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
            
            await app.initialize()
            await app.start()
            
            print("✅ Telegram Bot is online and listening...")
            
            # Use a longer polling interval to reduce conflict risk on fast reloads
            await app.updater.start_polling(drop_pending_updates=True, poll_interval=1.0)
            
            while True:
                await asyncio.sleep(5)
            
        except Exception as e:
            if "Conflict" in str(e):
                print("⚠️ Telegram Conflict: Instance already running. This task will exit to let the other live.")
            else:
                print(f"❌ Telegram Bot Error: {e}")
        finally:
            try:
                # Cleanup logic must be robust
                if 'app' in locals() and app.updater and app.updater.running:
                    await app.updater.stop()
                if 'app' in locals():
                    await app.stop()
                    await app.shutdown()
            except: 
                pass
            print("👋 Telegram Bot shut down.")

# Global instance to be imported in main.py
bot = TelegramBot()
