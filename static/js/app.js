const button1 = $('#button1');
const spinner = $('#spinner');
const img_list = $("#img_list");
const img_move = $('#img_move');
$('.f_button').click(async function () {
    const btn = $(this).attr('name');
    if (btn === "button1") {    //探すフォルダのボタンをクリック
        if ($('.img_label').length) {
            $('.img_label').remove();
            img_move.hide();
            $('.pagination-container').remove();
        }

        const url_param = new URLSearchParams(location.search);
        const param = url_param.get('search_word');
        const request = JSON.stringify({ param: param });

        button1.prop('disabled', true);
        spinner.show();

        await makeRequest(request);

        button1.prop('disabled', false);
        spinner.hide();
    }
    else {  // 移動先のフォルダを選択するボタンをクリック
        const checked = $('input:checked');
        let data = [];
        if (checked.length !== 0) {
            checked.each(function () {
                data.push({ check: $(this).val() });
            });
            const request = JSON.stringify(data);
            await makeRequest(request, checked);
        }
        else {
            alert("移動させたい画像を選んでください。");
        }
    }

    $('.pagination-container').remove();
    if ($('.img_label').length === 0) {
        img_move.hide();
    }
    else {
        pagination();
    }
});

async function makeRequest(request, ...args) {
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

    await $.ajax({
        url: '',
        headers: { 'X-CSRFToken': csrftoken },
        method: 'POST',
        dataType: 'json',
        data: request,
        contentType: 'application/json',
        async: true,
        cache: false,
    })
        .then(function (result) {
            console.log(result);
            if (result.folder !== "no") {
                if (result.img_files) {
                    // 画像を表示
                    showResult(result);
                }
                else if (result.move_file) {
                    // 移動させた画像を画面から削除
                    const checked = args[0];

                    let i = 0;
                    checked.each(function () {
                        //if (result.move_file[i] === "ok") {
                        $(this).parent().remove();
                        //}
                        //i++;
                    });

                    $('#move_text').text(`「${result.folder}」に、選択した画像ファイルを移動しました。`);
                }

                img_move.show();
            }
        })
        .catch(function (jqXHR, textStatus, errorThrown) {
            alert(`エラー${jqXHR.status}が発生しました。`);

            console.log(jqXHR.status);
            console.log(textStatus);
            console.log(errorThrown);
        });
}

// views.pyから返ってきた画像ファイルを表示
function showResult(result) {
    $('#folder_name').text(result["folder"]);
    $('#move_text').text('');

    if (result.img_files !== "no_files") {
        let img = '';
        const img_files = result["img_files"];
        const len = img_files.length;
        let i = 0;
        while (i < len) {
            img += `<label for='img${i + 1}' class='img_label col-md-3 text-center'>`
                + `<img src='${img_files[i].url}' class='img-thumbnail' style='height: 150px; width: auto'>`
                + `<input type='checkbox' value='${img_files[i].file_path}' id='img${i + 1}'
                    class='col-md-3 d-block mx-auto' checked>`
                + '</label>';
            i++;
        }
        img_list.append(img);
    }
    else {
        alert('画像ファイルが見つかりません。');
    }
}

// ページネーション
function pagination() {
    img_list.paginathing({
        perPage: 6,
        firstText: '最初',
        lastText: '最後',
        ulClass: 'pagination justify-content-center m-auto',
    });
}