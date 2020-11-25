$(()=>{
    let $addBtn = $('button.add');            // 模态框中的添加按钮
    let $form = $('#add-menu');               // 模态框中的表单

    $addBtn.click(()=>{
        $
            .ajax({
                url: '/myadmin/add_menu/',
                type: 'POST',
                data: $form.serialize()        // 将表单中所有字段序列化
            })
            .done((res)=>{
                if(res.errno === '0'){
                    // 添加成功，关闭模态框，并刷新一下菜单列表
                    $('#modal-add').modal('hide').on('hidden.bs.modal',  // 关闭模态框时触发事件
                        function (e) {
                            // 刷新菜单列表
                            $('#content').load(
                                $('.sidebar-menu li.active a').data('url'),      // url
                                (response, status, xhr)=>{
                                    if (status !== 'success'){
                                        message.showError('服务器超时，请重试!');
                                    }
                                }
                            )

                        })
                }else {
                    message.showError('添加菜单失败');
                    // 更新模态框中的表单信息
                    $('#modal-add .modal-content').html(res)
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！');
            })
    })
})