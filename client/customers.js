const customers = {} // содержит пары 'tokenChatGPT': isWorked
const proxy_customers = new Proxy(customers, {
    get(target, prop){
        if (prop in target) {
          return target[prop];
        } else {
          return false;
        }
    }
});


module.exports = proxy_customers;