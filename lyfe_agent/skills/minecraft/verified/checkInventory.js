/**
 * Checks the bot's inventory for a specific item and reports the quantity.
 * 
 * @param {*} bot - The Mineflayer bot instance.
 * @param {string} itemName - The name of the item to check in the inventory.
 * 
 * Example usage:
 * checkInventory(bot, 'diamond');
 */
function checkInventory(bot, itemName) {
    // Validate item name input
    if (typeof itemName !== "string") {
        bot.chat(`itemName must be a string`);
        return;
    }

    // Use mcData to ensure the item exists in Minecraft
    const itemByName = mcData.itemsByName[itemName];
    if (!itemByName) {
        bot.chat(`Item "${itemName}" does not exist in Minecraft.`);
        return;
    }

    // Find the item in the bot's inventory
    const item = bot.inventory.items().find(item => item.name === itemName);

    // Report the quantity of the item
    if (item) {
        bot.chat(`I have ${item.count} ${itemName}.`);
    } else {
        bot.chat(`I don't have any ${itemName}.`);
    }
}
