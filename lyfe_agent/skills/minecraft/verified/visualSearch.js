/**
 * Visually search for the nearest block of a specified type in the direction the bot is currently facing.
 * 
 * @param {Object} bot - The Mineflayer bot instance.
 * @param {string} itemName - The name of the block to search for (e.g., 'stone').
 * @returns The position of the nearest specified block in the direction the bot is facing, or null if not found.
 * 
 * Example usage:
 * visualSearch(bot, 'stone')
 */
function visualSearch(bot, itemName) {
    const maxDistance = 16; // Fixed maximum distance for the search

    // Calculate the direction vector from the bot's current yaw and pitch
    const yaw = bot.entity.yaw;
    const pitch = bot.entity.pitch;
    const direction = new Vec3(-Math.sin(yaw) * Math.cos(pitch), -Math.sin(pitch), -Math.cos(yaw) * Math.cos(pitch));

    // Find the nearest block of the specified type in the calculated direction
    const targetBlock = bot.findBlock({
        point: bot.entity.position,
        matching: block => block.name === itemName,
        maxDistance: maxDistance,
        count: 1,
        direction: direction.normalize() // Normalize the direction for a consistent search behavior
    });

    // Return the position of the target block if found, or null if not found
    if (targetBlock) {
        bot.lookAt(targetBlock.position);
        bot.chat(`I see a ${itemName} at ${targetBlock.position}`);
    }
    else {
        bot.chat(`I don't see ${itemName}`);
    }
        
    return targetBlock ? targetBlock.position : null;
}