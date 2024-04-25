/**
 * Equips an item by name.
 * 
 * @param {*} bot - The Mineflayer bot instance. Assume the bot is already spawned in the world.
 * @param {*} name - The name of the item to be equipped.
 * 
 * Example usage:
 * equipItem(bot, 'diamond_pickaxe');
 */
async function equipItem(bot, name) {
    // Validate input parameters
    if (typeof name !== "string") {
        throw new Error(`name for equipItem must be a string`);
    }
    
    // Look up the item in the Minecraft data to ensure it exists
    const itemByName = mcData.itemsByName[name];
    if (!itemByName) {
        bot.chat(`No Minecraft item named ${name}`);
        throw new Error(`No item named ${name}`);
    }
    
    // Find the item in the bot's inventory
    const item = bot.inventory.findInventoryItem(itemByName.id);
    if (!item) {
        bot.chat(`I don't have a ${name}`);
        return;
    }
    
    // Attempt to equip the item
    try {
        await bot.equip(item, 'hand');
        bot.chat(`Equipped ${name}`);
    } catch (err) {
        bot.chat(`Error equipping ${name}: ${err.message}`);
    }
}