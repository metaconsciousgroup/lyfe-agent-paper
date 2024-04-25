/**
 * Explore Minecraft world until items are found.
 * @param {*} bot - The Mineflayer bot instance. Assume the bot is already spawned in the world.
 * @param {*} name - The name of the item to be found.
 * @param {*} count - How many blocks of the item to find. Default is 1.
 * @param {*} maxTime - How long to explore for in seconds. Default is 60.
 * 
 * Example usage:
 * exploreUntil(bot, 'iron_ore');
 * exploreUntil(bot, 'oak_log', 3, 30);
 */
async function exploreUntil(bot, name, count = 1, maxTime = 60) {

    const callback = () => {
        const blocks = bot.findBlocks({
            matching: block => block.name === name,
            maxDistance: 16,  // TODO: Need to think about this value
            count: count
        });
        return blocks.length >= count ? blocks : null;
        };
    
    if (typeof maxTime !== "number") {
        throw new Error("maxTime must be a number");
    }
    if (typeof callback !== "function") {
        throw new Error("callback must be a function");
    }
    const test = callback();
    if (test) {
        bot.chat("Explore success.");
        return Promise.resolve(test);
    }

    maxTime = Math.min(maxTime, 60);
    return new Promise((resolve, reject) => {
        // Initialize the direction vector
        direction = getRandomDirection();

        let explorationInterval;
        let maxTimeTimeout;

        // Clean up the interval and timeout
        const cleanUp = () => {
            clearInterval(explorationInterval);
            clearTimeout(maxTimeTimeout);
            bot.pathfinder.setGoal(null);
        };

        // Explore until callback() returns true
        const explore = () => {
            // Perturb the direction vector by a small amount
            direction = perturbDirection(direction);
            // Move the bot in the specified direction
            moveBot(bot, direction);

            try {
                // Check if the callback returns true
                const result = callback();
                if (result) {
                    // If so, stop exploring
                    cleanUp();
                    bot.chat(`Explore success. Found ${name}.`);
                    resolve(result);
                }
            } catch (err) {
                cleanUp();
                reject(err);
            }
        };

        // Execute explore() every 1000 ms
        explorationInterval = setInterval(explore, 1000);

        // Stop exploring after maxTime seconds
        maxTimeTimeout = setTimeout(() => {
            cleanUp();
            bot.chat("Max exploration time reached");
            resolve(null);
        }, maxTime * 1000);
    });
}

function getRandomDirection() {
    // Return a random direction vector
    const theta = Math.random() * 2 * Math.PI;
    return theta;
}

function moveBot(bot, direction) {
    // Move the bot in the specified direction
    // Direction is the angle in radians in the XZ plane
    const { x, y, z } = bot.entity.position;
    distance = (Math.random() * 10 + 5);
    const newX = x + Math.sin(direction) * distance;
    const newY = y; // Maintain current vertical position
    const newZ = z + Math.cos(direction) * distance;
    const goal = new GoalNear(newX, newY, newZ);
    bot.pathfinder.setGoal(goal);
}

function perturbDirection(theta) {
    // Perturb the direction vector by a small amount
    const perturbation = 0.1;
    const deltaTheta = Math.random() * 2 * Math.PI;
    const newTheta = theta + deltaTheta * perturbation;
    // Bring the angle back to the range [0, 2pi)
    return newTheta % (2 * Math.PI);
}