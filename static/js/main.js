function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const items = document.getElementsByClassName('like-section')
for (let item of items){
    const btnlike = item.children[0].children[0]
    const raiting = item.children[1].children[0]
    const btndislike = item.children[2].children[0]
    const formData = new FormData();
    formData.append('id', btnlike.dataset.id)
    formData.append('type', 'question')
    formData.append('vote', 0)
    const request = new Request('/like/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    fetch(request)
        .then((response)=>response.json())
        .then((data)=>{
            console.log(data);
            if (data.liked){
                btnlike.classList.remove('btn-outline-success');
                btndislike.classList.remove('btn-outline-danger');
                btnlike.classList.add('btn-success');
                btndislike.classList.add('btn-danger');
            }
        })
    btnlike.addEventListener('click', function () {
        const formData = new FormData();
        formData.append('id', btnlike.dataset.id)
        formData.append('type', 'question')
        formData.append('vote', 1)
        const request = new Request('/like/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        fetch(request)
            .then((response)=>response.json())
            .then((data)=>{
                console.log(data);
                raiting.innerHTML = data.count;
                if (data.liked){
                    btnlike.classList.remove('btn-outline-success');
                    btndislike.classList.remove('btn-outline-danger');
                    btnlike.classList.add('btn-success');
                    btndislike.classList.add('btn-danger');
                }
                else{
                    btnlike.classList.add('btn-outline-success');
                    btndislike.classList.add('btn-outline-danger');
                    btnlike.classList.remove('btn-success');
                    btndislike.classList.remove('btn-danger');
                }
            })
    })
    btndislike.addEventListener('click', function () {
        const formData = new FormData();
        formData.append('id', btndislike.dataset.id)
        formData.append('type', 'question')
        formData.append('vote', -1)
        const request = new Request('/like/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        fetch(request)
            .then((response)=>response.json())
            .then((data)=>{
                console.log(data);
                raiting.innerHTML = data.count;
                if (data.liked){
                    btnlike.classList.remove('btn-outline-success');
                    btndislike.classList.remove('btn-outline-danger');
                    btnlike.classList.add('btn-success');
                    btndislike.classList.add('btn-danger');
                }
                else{
                    btnlike.classList.add('btn-outline-success');
                    btndislike.classList.add('btn-outline-danger');
                    btnlike.classList.remove('btn-success');
                    btndislike.classList.remove('btn-danger');
                }
            })
    })
}
const answers = document.getElementsByClassName('answer-like-section')
for (let item of answers){
    const btnlike = item.children[0].children[0]
    const raiting = item.children[1].children[0]
    const btndislike = item.children[2].children[0]
    const formData = new FormData();
    formData.append('id', btnlike.dataset.id)
    formData.append('type', 'answer')
    formData.append('vote', 0)
    const request = new Request('/like/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    fetch(request)
        .then((response)=>response.json())
        .then((data)=>{
            console.log(data);
            if (data.liked){
                btnlike.classList.remove('btn-outline-success');
                btndislike.classList.remove('btn-outline-danger');
                btnlike.classList.add('btn-success');
                btndislike.classList.add('btn-danger');
            }
        })
    btnlike.addEventListener('click', function () {
        const formData = new FormData();
        formData.append('id', btnlike.dataset.id)
        formData.append('type', 'answer')
        formData.append('vote', 1)
        const request = new Request('/like/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        fetch(request)
            .then((response)=>response.json())
            .then((data)=>{
                console.log(data);
                raiting.innerHTML = data.count;
                if (data.liked){
                    btnlike.classList.remove('btn-outline-success');
                    btndislike.classList.remove('btn-outline-danger');
                    btnlike.classList.add('btn-success');
                    btndislike.classList.add('btn-danger');
                }
                else{
                    btnlike.classList.add('btn-outline-success');
                    btndislike.classList.add('btn-outline-danger');
                    btnlike.classList.remove('btn-success');
                    btndislike.classList.remove('btn-danger');
                }
            })
    })
    btndislike.addEventListener('click', function () {
        const formData = new FormData();
        formData.append('id', btndislike.dataset.id)
        formData.append('type', 'answer')
        formData.append('vote', -1)
        const request = new Request('/like/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        fetch(request)
            .then((response)=>response.json())
            .then((data)=>{
                console.log(data);
                raiting.innerHTML = data.count;
                if (data.liked){
                    btnlike.classList.remove('btn-outline-success');
                    btndislike.classList.remove('btn-outline-danger');
                    btnlike.classList.add('btn-success');
                    btndislike.classList.add('btn-danger');
                }
                else{
                    btnlike.classList.add('btn-outline-success');
                    btndislike.classList.add('btn-outline-danger');
                    btnlike.classList.remove('btn-success');
                    btndislike.classList.remove('btn-danger');
                }
            })
    })
}
const corrects = document.getElementsByClassName('answer-correct')
for (let correct of corrects){
    const check = correct.children[0]
    console.log(check)
    check.addEventListener('change', function () {
        const formData = new FormData();
        formData.append('answerid', check.dataset.answerid)
        formData.append('questionid', check.dataset.questionid)
        const request = new Request('/correct/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        fetch(request)
            .then((response)=>response.json())
            .then((data)=>{
                console.log(data);
                if (data.success!=1){
                    alert('It is not yours question!');
                    if (data.correct==1){
                        check.checked=False;
                    }
                    else{
                        check.checked=True;
                    }
                }
            })
    })
}