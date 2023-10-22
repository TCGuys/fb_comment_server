
let stateButton = () => {
  let allowClickButton = true;
  let btn = document.querySelector('#delete-button');
  const allow = () => {
    allowClickButton = true;
    btn.classList.add('allow');
    btn.classList.remove('prohibit');
  }
  const prohibit = () => {
    allowClickButton = false;
    btn.classList.remove('allow');
    btn.classList.add('prohibit')
  }
  const isAllow = () => allowClickButton;

  return {
    allow,
    prohibit,
    isAllow,
  }
}

let {allow, prohibit, isAllow} = stateButton();
function replacePlaceholder(inputId, value) {
  var inputElement = document.getElementById(inputId);
  inputElement.placeholder = value;
}

async function deleteNegativeComments() {
  if(!isAllow()) return;
  else prohibit();

  let facebook_token = document.getElementById('facebook_token').value;
  let gpt_token = document.getElementById('gpt_token').value;

  let data = {
    facebook_token,
    gpt_token,
  };

  try{
    let response = await  fetch('/process_post_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    let result = await response.json();
    console.log(result)
    if(!result.Success) throw new Error(result);
    showAnswer(true)
  }catch(error){
    showAnswer(false)
    console.info(error)
  }finally {
    allow();
  }
}

function showAnswer(ans){
  let field = document.querySelector('.answer');
  field.classList.add(ans ? 'success' : 'error');
  field.innerHTML = ans ? '<p>SUCCESS</p>' : '<p>ERROR</p>';


  setTimeout(function(){
    field.classList.remove(ans ? 'success' : 'error');
  }, 3000);
}
