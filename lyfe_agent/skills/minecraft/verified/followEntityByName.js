/**
 * Follows a specified entity.
 * 
 * @param {*} bot - The Mineflayer bot instance. Assume the bot is already spawned in the world.
 * @param {*} entityName - The name of the entity to follow.
 * @param {*} distance - The desired distance to keep from the entity. Default is 3 blocks.
 * 
 * Example usage:
 * followEntity(bot, "PlayerName", 3);
 */
function followEntityByName(bot, entityName, distance = 3) {

    const entity = findEntityByName(bot, entityName);
    
    if (!entity) {
        bot.chat(`Entity ${entityName} not found.`);
        return;
    }

    // Stop any existing follow behavior
    if (bot.pathfinder.goal) bot.pathfinder.setGoal(null);

    // Define a dynamic goal that updates with the entity's position
    const followGoal = new GoalFollow(entity, distance);
    bot.pathfinder.setGoal(followGoal, true); // The second argument true makes the goal dynamic

    bot.chat(`Following entity ID ${entity.id}`);
    
    // Optionally, handle events like losing sight of the entity
    bot.on('physicsTick', checkDistance);
    
    function checkDistance() {
        if (!entity || !bot.entities[entity.id]) {
            bot.chat("Lost sight of the entity. Stopping follow.");
            bot.pathfinder.setGoal(null);
            bot.removeListener('physicsTick', checkDistance); // Clean up the event listener
        }
    }
}


/**
 * Finds a player entity by username.
 * 
 * @param {*} bot - The Mineflayer bot instance.
 * @param {string} name - The name of the entity to find.
 */
function findEntityByName(bot, name) {
    return Object.values(bot.entities).find(entity => entity.username === name);
}