/**
 * Drops a specified item from the bot's inventory on the ground.
 * 
 * @param {Object} bot - The Mineflayer bot instance.
 * @param {string} itemName - The name of the item to drop.
 * @param {number} count - The number of items to drop. Defaults to 1 if not specified.
 * 
 * Example usage:
 * dropItem(bot, 'dirt', 3);
 */
async function dropItem(bot, itemName, count = 1) {
    // Find the item in the bot's inventory
    const itemToDrop = bot.inventory.items().find(item => item.name === itemName);

    if (!itemToDrop) {
        console.log(`I don't have '${itemName}'.`);
        return;
    }

    try {
        // Drop the item
        await bot.toss(itemToDrop.type, null, count);
        console.log(`Dropped ${count} ${itemName}.`);
    } catch (err) {
        console.error(`Failed to drop ${itemName}:`, err);
    }
}

