$(()=>{
    let $course_data = $('.course-data');        // 获取隐藏的span对象
    let sVideoUrl = $course_data.data('video-url');         // 拿到data-video-url属性值
    let sCoverUrl = $course_data.data('cover-url');         // 拿到data-cover-url属性值
    let player = cyberplayer("course-video").setup({
        width: '100%',
        height: 650,
        file: sVideoUrl,
        image: sCoverUrl,
        autostart: false,
        stretching: "uniform",
        repeat: false,
        volume: 100,
        controls: true,
        ak: 'd82e84ed97064b8f9df80c138c98f87d'
    });
})