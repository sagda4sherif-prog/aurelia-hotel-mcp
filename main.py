import asyncio
import sys
from agent.client import AureliaAgent
from agent.config import load_config


async def main() -> None:
    # 1.load configuration from environment variables and .env file
    try:
        config = load_config()
    except Exception as e:
        print(f"Configuration error: {e}")
        return

    print("=" * 60)
    print("Connecting Aurelia Agent to MCP Server...")
    print("=" * 60)

    try:
        # 2. open a connection to the server and start the agent
        async with AureliaAgent(config) as agent:
            print("\nConnected successfully!")
            print(
                f"Loaded Tools ({len(agent.tools)}): {[t.name for t in agent.tools]}"
            )

            if agent.resources:
                print(
                    f"Loaded Resources ({len(agent.resources)}): {[r.uri for r in agent.resources]}"
                )

            print("\n" + "=" * 60)
            print("Aurelia Hotel AI Assistant is Ready!")
            print("Type your message below. (Type 'exit', 'quit', or 'q' to stop)")
            print("=" * 60 + "\n")

            # 3.(Interactive Chat Loop)
            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\nSession ended. Goodbye!")
                    break

                # ignore empty inputs
                if not user_input:
                    continue

                #exit the loop if the user types exit, quit, or q
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nClosing connection. Goodbye!")
                    break

                print("\nThinking...")
                try:
                    # processing the user input and getting the response from the agent
                    response = await agent.run_turn(user_input)
                    print("-" * 60)
                    print(f"Aurelia:\n{response}")
                    print("-" * 60 + "\n")
                except Exception as turn_err:
                    print(f"Error during turn execution: {turn_err}\n")

                # wait for any pending notifications before next input
                await agent.wait_for_pending_notifications()

    except Exception as conn_err:
        print(f"\nConnection or Handshake failed: {conn_err}")


if __name__ == "__main__":
    asyncio.run(main())