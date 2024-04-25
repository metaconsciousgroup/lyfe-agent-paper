/**
 * Places an item at a specified position relative to the bot's current position and orientation.
 * The function calculates an adjusted position based on the bot's yaw (direction it is facing) and attempts
 * to find a suitable reference block nearby that the item can be placed against.
 *
 * @param {Object} bot - The Mineflayer bot instance. Assume the bot is already spawned in the world.
 * @param {string} name - The name of the item to be placed. Must correspond to an item in the bot's inventory.
 * @param {Vec3} relativePosition - The position where the item will be placed, relative to the bot's own position and orientation.
 * 
 * Example Usage:
 * // To place a crafting table 2 blocks to the right and 1 blocks forward relative to the bot's current orientation:
 * placeItem(bot, 'crafting_table', new Vec3(2, 0, 1));
 *
 */
async function placeItem(bot, name, relativePosition) {
    if (typeof name !== "string") throw new Error(`'name' must be a string`);

    const itemByName = mcData.itemsByName[name];
    if (!itemByName) throw new Error(`No item named '${name}' found`);

    const item = bot.inventory.findInventoryItem(itemByName.id);
    if (!item) {
        bot.chat(`I don't have a ${name} in my inventory.`);
        return;
    }

    // Calculate the adjusted position based on the bot's orientation
    const yaw = bot.entity.yaw;
    const forward = new Vec3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new Vec3(-forward.z, 0, forward.x);
    const adjustedPosition = bot.entity.position.add(forward.scaled(relativePosition.z)).add(right.scaled(relativePosition.x)).add(new Vec3(0, relativePosition.y, 0));

    // Find a suitable reference block to place the item against
    let referenceBlock = null, faceVector = null;
    const faceVectors = [
        new Vec3(0, 1, 0),  // top
        new Vec3(0, -1, 0), // bottom
        new Vec3(1, 0, 0),  // sides
        new Vec3(-1, 0, 0),
        new Vec3(0, 0, 1),
        new Vec3(0, 0, -1),
    ];

    for (const vector of faceVectors) {
        const testPos = adjustedPosition.minus(vector);
        const block = bot.blockAt(testPos);
        if (block && block.type !== 0) { // Check if block is not air (type 0)
            referenceBlock = block;
            faceVector = vector;
            bot.chat(`Placing ${name} on ${block.name} at ${block.position}`);
            break;
        }
    }

    if (!referenceBlock) {
        bot.chat(`No suitable location found to place ${name}.`);
        return;
    }

    // Attempt to place the item
    try {
        // await bot.pathfinder.goto(new GoalNear(referenceBlock.position.x, referenceBlock.position.y, referenceBlock.position.z, 1));
        await bot.pathfinder.goto(new GoalPlaceBlock(adjustedPosition, bot.world, {}));
        await bot.equip(item, "hand");
        await bot.placeBlock(referenceBlock, faceVector);
        bot.chat(`Placed ${name} successfully.`);
    } catch (err) {
        bot.chat(`Failed to place ${name}: ${err.message}`);
    }
}