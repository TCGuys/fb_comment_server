const fetch = require('node-fetch');
const express = require('express');
const customers = require('./customers');
const app = express();
const URL = 'http://91.247.37.218:5000';
app.use(express.json());
app.use(express.static('public'));
app.get('/', function (request, response) {
    response.sendFile(__dirname + '/public/index.html');
});

app.post('/process_post_data', async (req, res) => {
    let {gpt_token} = req;

    if(customers[gpt_token]){
        res.json({Success: 'WORKED'})
        return;
    }

    customers[gpt_token] = true;
    let getAnswer = async () => {
        let response = await fetch(URL + '/process_post_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req.body)
        });

        let ans = await response.json();
        customers[gpt_token] = false;
        res.json(ans);
    }
    return await getAnswer();
});

app.get('/is_worked', (req, res) => {
    let {gpt_token} = req;
    res.json(customers[gpt_token]);
})

// app.get('/get_hello', async (req, res) => {
//     res.json(customers.hello)
// });
//
// app.get('/hello', async (req, res) => {
//     customers.hello = true;
//     let result = setTimeout(() => {
//         customers.hello = false;
//         res.json('HELLO');
//     }, 10000)
// });

app.listen(3000);
