$(()=>{
    let $deleteBtns = $('button.delete');    // 删除按钮（组）
    menuId = 0;                          // 被点击菜单Id, let声明为局部对象，其他js不能使用，不用let或var声明，则为页面全局变量
    let $currentMenu = null;                 // 当前被点击菜单对象

    $deleteBtns.click(function(){
        let $this = $(this);
        $currentMenu = $this.parent().parent();             // .parent()-->td .parent() -->tr
        menuId = $this.parent().data('id');

        let menuName = $this.parent().data('name');
        // 改变模态框的显示内容
        $('#modal-delete .modal-body p').html('确定删除菜单：《' + menuName + '》？');
        // 显示模态框
        $('#modal-delete').modal('show');
    });

    // 点击模态框的确定删除按钮，发送ajax删除
    $('#modal-delete button.delete-confirm').click(()=>{
        deleteMenu();
    });

    // 删除菜单的函数
    function deleteMenu(){
        $
            .ajax({
                url: '/myadmin/menu/' + menuId + '/',
                type: 'DELETE',
                dataType: 'json'
            })
            .done((res)=>{
                if (res.errno === '0'){
                    // 关闭模态框
                    $('#modal-delete').modal('hide');
                    // 删除菜单元素
                    $currentMenu.remove();
                    message.showSuccess(res.errmsg)
                }else if(res.errno ==='4105'){
                    message.showError(res.errmsg)
                }else if(res.errno === '4101'){
                    message.showError(res.errmsg);
                    setTimeout(()=>{
                        window.location.href = res.data.url
                    }, 1500)
                }else{
                    message.showError(res.errmsg)
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
            })
    }

    // 编辑功能
    let $editBtns = $('button.edit');
    $editBtns.click(function(){
        let $this = $(this);
        $currentMenu = $this.parent().parent();
        menuId = $this.parent().data('id');
        // let menuName = $this.parent().data('name');

        // 发送ajax，返回的不是json数据
        $
            .ajax({
                url: '/myadmin/menu/' + menuId + '/',
                type: 'GET'
            })
            .done((res)=>{
                if(res.errno ==='4105'){
                    message.showError(res.errmsg)
                }else if(res.errno === '4101'){
                    message.showError(res.errmsg);
                    setTimeout(()=>{
                        window.location.href = res.data.url
                    }, 1500)
                }else{
                    // 改变模态框内容
                    $('#modal-update .modal-content').html(res);      // 返回add_menu.html中的内容
                    // 显示模态框
                    $('#modal-update').modal('show')
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
            })
    })
});