const fetch = require('node-fetch');
const express = require('express')
const path = require('path');
const customers = require('./customers');
const app = express();
const URL = 'http://185.190.250.9:5000';
app.use(express.json());
app.use('/public', express.static( './public'));
app.get('/', function (request, response) {
    console.log(path.join(__dirname, '/index.html'));
    response.sendFile(__dirname + '/index.html');
});

app.post('/process_post_data', async (req, res) => {
    let {gpt_token} = req;

    if(customers[gpt_token]){
        res.json({Success: 'WORKED'})
        return;
    }

    customers[gpt_token] = true;
    let getAnswer = async () => {
        try{
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
        }catch (e){
            customers[gpt_token] = false;
            res.json({Success: false, error: ans});
        }

    }
    return await getAnswer();
});
const PORT= 5173;
const HOST = '0.0.0.0';
app.listen(PORT, HOST, () => console.log('server started on port ' + PORT));

