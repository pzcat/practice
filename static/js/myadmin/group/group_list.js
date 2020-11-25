$(()=>{
    // 点击第一列进入详情页
    $('tr').each(function(){
        $(this).children('td:first').click(function(){
            $('#content').load(
                $(this).data('url'),
                (response, status, xhr)=>{
                    if (status !== 'success'){
                        message.showError('服务器超时，请重试！')
                    }
                }
            );
        })
    });

    // 添加分组
    $('.box-tools button').click(function () {
        $('#content').load(
                $(this).data('url'),
                (response, status, xhr) => {
                    if (status !== 'success') {
                        message.showError('服务器超时，请重试！')
                    }
                }
            );

    });
})