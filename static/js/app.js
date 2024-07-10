const image = $('#image');
image.on('click', async function() {
    const canvas = document.getElementById('preview');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if ($('.list-group-item').length) {
        $('.list-group-item').remove();
    }
    image.prop('disabled', true);
    $('#spinner1').show();

    await $.ajax({
            url: 'image/',
            method: 'GET'
        })
        .then(function(result) {
            const file = result.file;
            $('#file_name').text(file);

            if (file && !result.error) {
                if (ctx) {
                    const img = new Image();
                    img.src = result.file_url;

                    img.onload = function() {
                        canvas.width = img.width;
                        canvas.height = img.height;

                        ctx.drawImage(img, 0, 0);

                        let line_width = '';
                        let font_size = '';
                        if (canvas.width <= 1200 || canvas.height <= 1200) {
                            if (canvas.width <= 700 || canvas.height <= 700) {
                                line_width = 3;
                                font_size = '20px';
                            } else {
                                line_width = 6;
                                font_size = '50px';
                            }
                        } else {
                            line_width = 15;
                            font_size = '140px';
                        }

                        // Pythonから返ってきた物体検出のバウンディングボックスを画像に描画
                        for (const value of result.names.reverse()) {
                            ctx.lineWidth = line_width;
                            ctx.strokeStyle = `rgb(
                                ${value.color[0]},
                                ${value.color[1]},
                                ${value.color[2]})`;

                            ctx.strokeRect(
                                value.box[0],
                                value.box[1],
                                value.box[2],
                                value.box[3]
                            );

                            ctx.fillStyle = ctx.strokeStyle;
                            ctx.textBaseline = 'top';
                            ctx.textAlign = 'left';
                            ctx.font = `${font_size} sans-serif`;
                            ctx.fillText(
                                value.name,
                                value.box[0],
                                value.box[1]
                            );
                        }
                    };
                } else {
                    $('#img')
                        .attr('src', result.file_url)
                        .addClass('img-thumbnail');
                }

                let obj = '';
                if (result.names !== 'no') {
                    for (const value of result.names) {
                        obj += `<a href='search/?search_word=${value.name}' class='list-group-item list-group-item-action list-group-item-warning'>${value.name}`;
                    }

                    $('.list-group').append(obj);
                } else {
                    alert(
                        '画像に写っている対象が検出できませんでした。画像の変更をお願いします。'
                    );
                }
            } else if (file && result.error) {
                alert('選択したファイルは開くことができません。');
            }
        })
        .catch(function(jqXHR, textStatus, errorThrown) {
            alert(`エラー${jqXHR.status}が発生しました。`);

            console.log(jqXHR.status);
            console.log(textStatus);
            console.log(errorThrown);
        });

    image.prop('disabled', false);
    $('#spinner1').hide();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const file_list = $('#file_list');
const file_move = $('#file_move');

$('.f_button').on('click', async function() {
    const btn = $(this).attr('name');

    if (btn === 'button1') {
        //探すフォルダのボタンをクリック

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

        $('#button1').prop('disabled', true);
        $('#spinner2').show();

        await makeRequest(request);

        $('#button1').prop('disabled', false);
        $('#spinner2').hide();
    } else {
        // 移動先のフォルダを選択するボタンをクリック
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
            contentType: 'application/json'
        })
        .then(function(result) {
            if (result.folder && result.img_files) {
                $('#folder_name').text(result.folder);
                $('#move_text').text('');

                // 画像を表示
                showResult(result);
            } else if (result.folder && result.move_files) {
                const checked = args[0];
                checked.each(function() {
                    // 移動させた画像を画面から削除
                    $(this)
                        .parent()
                        .remove();
                });

                $('#move_text').text(
                    `「${result.folder}」に、選択した画像ファイルを移動しました。`
                );
            }

            file_move.show();
        })
        .catch(function(jqXHR, textStatus, errorThrown) {
            alert(`エラー${jqXHR.status}が発生しました。`);

            console.log(jqXHR.status);
            console.log(textStatus);
            console.log(errorThrown);
        });
}

// views.pyから返ってきた画像ファイルを表示
function showResult(result) {
    const img_files = result.img_files;

    if (img_files !== 'no_files') {
        let len = img_files.length;
        if (len) {
            let img = '';
            let i = 0;
            while (i < len) {
                if (img_files[i].error) {
                    setTimeout(() => {
                        alert(img_files[i].error);
                    }, 0);
                    break;
                }

                // prettier-ignore
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