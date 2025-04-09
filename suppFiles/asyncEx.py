import asyncio

async def print_B(): #Simple async def
    print("B")

async def main_def():
    print("A")
    await asyncio.gather(print_B())
    print("C")
asyncio.run(main_def())

# The function you wait for must include async
# The function you use await must include async
# The function you use await must run by asyncio.run(THE_FUNC())




