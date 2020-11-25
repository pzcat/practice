$(() => {
    // 上传封面
    // 上传文件input
    let $fileInput = $('.input-group-btn input');
    let $uploadBtn = $('.input-group-btn button');
    $uploadBtn.click(function () {
            $fileInput.click()
        }
    );
    // 自动上传文件
    $fileInput.change(function () {
        $this = $(this);
        if ($this.val() !== ''){                // 选中文件后才触发上传动作
            let formData = new FormData();
            formData.append('upload', $this[0].files[0]);
            formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
            $
                .ajax({
                    url: '/myadmin/upload/',
                    // 使用ckeditor_uploader 就使用下面的url
                    // url: '/ckeditor/upload/&responseType=json',
                    type: 'POST',
                    data: formData,
                    processData: false,              // 不进行格式化
                    contentType: false
                })
                .done((res)=>{
                    if (res.data.uploaded === '1'){
                        message.showSuccess('封面图片上传成功！');
                        $('input[name="image_url"]').val(res.data.url);
                        // 清空一下
                        $this.val('')
                    }else{
                        message.showError('封面图片上传失败！')
                    }
                })
                .fail(()=>{
                    message.showError('服务器超时, 请重新尝试！')
                })
        }
    });
    // 返回按钮
    $('.box-footer button.back').click(() => {
        $('#content').load(
            $('.sidebar-menu li.active a').data('url'),
            (response, status, xhr) => {
                if (status !== 'success') {
                    message.showError('服务器超时，请重试！')
                }
            }
        );
    });

    // 保存按钮
    $('.box-footer button.save').click(function () {
        // 更新富文本编辑器内容到form表单
        window.window.CKEDITOR.instances.id_content.updateElement();
        $
            .ajax({
                url: $(this).data('url'),
                data: $('form').serialize(),
                type: $(this).data('type')
            })
            .done((res) => {
                if (res.errno === '0') {
                    message.showSuccess(res.errmsg);
                    $('#content').load(
                        $('.sidebar-menu li.active a').data('url'),
                        (response, status, xhr) => {
                            if (status !== 'success') {
                                message.showError('服务器超时，请重试！')
                            }
                        }
                    );
                } else {
                    $('#content').html(res)
                }
            })
            .fail((res) => {
                message.showError('服务器超时，请重试！')
            })
    })

});