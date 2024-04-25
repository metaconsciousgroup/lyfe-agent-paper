/* Play around */

// TEMPORARY
runBot(bot);

async function runBot(bot) {
    bot.chat('/give @a minecraft:crafting_table 1');
    bot.chat('/give @a minecraft:cobblestone 10');
    bot.chat('/give @a minecraft:oak_planks 10');

    const bot_inventory = bot.inventory.items();
    console.log('Bot inventory:')
    console.log(bot_inventory)
    
    try {
        // Usage example (assuming 'bot' is your Mineflayer bot instance)
        console.log("Placing cobblestone")
        await placeItemInFront(bot, "cobblestone");
    } catch (err) {
        console.error(err);
    }      
    }
        
        
async function placeItemInFront(bot, itemName) {
    // Find the item in the bot's inventory by name
    const itemToPlace = bot.inventory.items().find(item => item.name === itemName);
    
    if (!itemToPlace) {
        console.log("No item to place")
        return;
    }
    
    // Get the block position directly in front of the bot
    const referenceBlock = bot.blockAt(bot.entity.position.offset(2, -1, 2));
    if (referenceBlock && referenceBlock.name === 'air') {
        console.log('Cannot place a block in the air. Please ensure the bot is facing a solid block.');
        return;
    }
    // Equip the item in the bot's hand
    console.log("Equipping item")
    await bot.equip(itemToPlace, 'hand');
    
    // Place the item in front of the bot
    try {
        // Place item on top of the reference block
        console.log("Placing cobblestone on Block")
        await bot.placeBlock(referenceBlock, new Vec3(0, 1, 0));
    } catch (err) {
    }
}

