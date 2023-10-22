const fetch = require('node-fetch');
const express = require('express');
const app = express();
const URL = 'http://91.247.37.218:5000';
app.use(express.json());
app.use(express.static('public'));
app.get('/', function (request, response) {
    response.sendFile(__dirname + '/public/index.html');
});

app.post('/process_post_data', async (req, res) => {
    let getAnswer = async () => {
        let response = await fetch(URL + '/process_post_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req.body)
        });
        let ans = await response.json();
        res.json(ans);
    }
    return await  getAnswer();
});

app.listen(3000);
