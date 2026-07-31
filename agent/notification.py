import asyncio
from typing import Any
from mcp import types

async def handle_message(
        agent,
        message: Any,
    ) -> None:
        """Generic server->client message handler.

        Only ServerNotification instances are interesting here (requests are
        handled by the dedicated sampling/elicitation callbacks above, and a
        bare Exception means the read loop itself broke). We only act on
        ToolListChangedNotification: Aurelia's server fires it exactly once,
        when a session authenticates as duty-manager and approve_compensation
        (and other manager-tier tools) become callable - so on receipt we
        refresh the catalog instead of polling list_tools() on a timer or,
        worse, assuming the tool list we cached at startup is still correct.
        """
        if isinstance(message, Exception):
            print(f"[notifications] transport error: {message}")
            return

        if not isinstance(message, types.ServerNotification):
            return  # server-initiated *requests* go through their own callbacks

        notification = message.root
        if isinstance(notification, types.ToolListChangedNotification):
            print("[notifications] tools/list_changed received -> refreshing catalog")
            
            agent._pending_notification_tasks.append(asyncio.create_task(agent.refresh_catalog()))
        elif isinstance(notification, types.LoggingMessageNotification):
            print(f"[server log:{notification.params.level}] {notification.params.data}")
        