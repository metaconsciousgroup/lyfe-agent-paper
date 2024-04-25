/**
 * Mine a block by name in Minecraft.
 * 
 * @param {*} bot - The Mineflayer bot instance. Assume the bot is already spawned in the world.
 * @param {*} name - The name of the block to be mined.
 * @param {*} count - How many blocks of the item to mine. Default is 1.
 * 
 * Example usage:
 * mineBlock(bot, 'cobblestone', 5);
 */
async function mineBlock(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new Error(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new Error(`count for mineBlock must be a number`);
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }
    // Find blocks within 32 blocks of the bot, return up to 64 blocks
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 32,
        count: 64,
    });
    // If no blocks found, return
    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        _mineBlockFailCount++;
        if (_mineBlockFailCount > 10) {
            throw new Error(
                "mineBlock failed too many times, make sure you explore before calling mineBlock"
            );
        }
        return;
    }
    // Convert block positions to block objects
    const targets = [];
    for (let i = 0; i < blocks.length; i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    // Mine the blocks using the collectBlock plugin.
    // Allow the bot to mine blocks that are not directly reachable.
    await bot.collectBlock.collect(targets, {
        ignoreNoPath: true,
        count: count,
    });
}