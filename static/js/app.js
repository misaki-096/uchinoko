$('#image').click(function() {

    if ($('.list-group-item').length) {
        $('.list-group-item').remove();
    }

    $.ajax({
        url: 'image/',
        method: 'GET',
        //cache: false
    }).then(function(result) {
        console.log(result.names);
        const file = result.file

        if (file !== 'no' && file !== 'error') {
            $('#img').attr('src', result.file_url).addClass('img-thumbnail');
            //$('#img').getContext('2d')
            $('#file_name').text(file);

            let obj = '';
            if (result.names !== 'no') {

                for (const value of result.names) {
                    obj += `<a href='search/?search_word=${value.name}' class='list-group-item list-group-item-action list-group-item-warning'>${value.name}`;
                }
                $('.list-group').append(obj);

            } else {
                alert('画像に写っている対象が検出できませんでした。画像の変更をお願いします。');
            }

        } else if (file === 'error') {
            alert('選択したファイルは開くことができません。');
        }

    }).catch(function(jqXHR, textStatus, errorThrown) {
        alert(`エラー${jqXHR.status}が発生しました。`);

        console.log(jqXHR.status);
        console.log(textStatus);
        console.log(errorThrown);
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const button1 = $('#button1');
const spinner = $('#spinner');
const file_list = $('#file_list');
const file_move = $('#file_move');

$('.f_button').click(async function() {
    const btn = $(this).attr('name');

    if (btn === 'button1') { //探すフォルダのボタンをクリック

        if ($('.img_label').length) {
            $('.img_label').remove();
            file_move.hide();
            $('.pagination-container').remove();
        }

        const yolo = $('input[name="yolo"]:checked').val();

        const url_param = new URLSearchParams(location.search);
        const param = url_param.get('search_word');
        const request = JSON.stringify({
            param: param,
            yolo: yolo
        });

        button1.prop('disabled', true);
        spinner.show();

        await makeRequest(request);

        button1.prop('disabled', false);
        spinner.hide();

    } else { // 移動先のフォルダを選択するボタンをクリック
        const checked = $('input[name="files"]:checked');
        let data = [];
        if (checked.length !== 0) {
            checked.each(function() {
                data.push({
                    check: $(this).val()
                });
            });
            const request = JSON.stringify(data);

            await makeRequest(request, checked);

        } else {
            alert('移動させたい画像を選んでください。');
        }
    }

    $('.pagination-container').remove();
    if ($('.img_label').length === 0) {
        file_move.hide();
    } else {
        pagination();
    }
});

async function makeRequest(request, ...args) {
    await $.ajax({
        url: '',
        headers: {
            'X-CSRFToken': csrftoken
        },
        method: 'POST',
        dataType: 'json',
        data: request,
        contentType: 'application/json',
        async: true,
        cache: false

    }).then(function(result) {
        if (result.folder !== 'no') {
            if (result.img_files) {
                // 画像を表示
                showResult(result);

            } else if (result.move_files) {
                const checked = args[0];
                let i = 0;
                checked.each(function() { // 移動させた画像を画面から削除
                    $(this).parent().remove();
                });

                $('#move_text').text(`「${result.folder}」に、選択した画像ファイルを移動しました。`);
            }

            file_move.show();
        }
    }).catch(function(jqXHR, textStatus, errorThrown) {
        alert(`エラー${jqXHR.status}が発生しました。`);

        console.log(jqXHR.status);
        console.log(textStatus);
        console.log(errorThrown);
    });
}

// views.pyから返ってきた画像ファイルを表示
function showResult(result) {
    $('#folder_name').text(result.folder);
    $('#move_text').text('');
    const img_files = result.img_files;

    if (img_files !== 'no_files') {
        const len = img_files.length;
        if (len) {
            let img = '';
            let i = 0;
            while (i < len) {
                img += `<label for='img${i + 1}' class='img_label col-md-3 text-center'>
                        <img src='${img_files[i].url}' class='img-thumbnail' style='height: 150px; width: auto'>
                        <input type='checkbox' value='${img_files[i].file_path}' id='img${i + 1}'
                        class='col-md-3 d-block mx-auto' name='files' checked>
                        </label>`;
                i++;
            }
            file_list.append(img);
        } else {
            alert('探したい画像が見つかりませんでした。');
        }
    } else {
        alert('画像ファイルが見つかりません。');
    }
}

// ページネーション
function pagination() {
    file_list.paginathing({
        perPage: 8,
        firstText: '最初',
        lastText: '最後',
        ulClass: 'pagination justify-content-center m-auto'
    });
}