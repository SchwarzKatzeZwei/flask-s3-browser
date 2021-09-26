function copyTextToClipboard(textVal) {
    // テキストエリアを用意する
    var copyFrom = document.createElement("textarea");
    // テキストエリアへ値をセット
    copyFrom.textContent = textVal;

    // bodyタグの要素を取得
    var bodyElm = document.getElementsByTagName("body")[0];
    // 子要素にテキストエリアを配置
    bodyElm.appendChild(copyFrom);

    // テキストエリアの値を選択
    copyFrom.select();
    // コピーコマンド発行
    var retVal = document.execCommand('copy');
    // 追加テキストエリアを削除
    bodyElm.removeChild(copyFrom);
    // 処理結果を返却
    return retVal;
}

function get_public_url(key) {
    let formData = new FormData();
    formData.append('key', key);
    fetch("/get_public_url", {
        method: "POST",
        body: formData,
    })
        .then(function (response) {
            return response.text();  // ここのtextをjsonやblobに変えると取得形式が変わる
        })
        .then(function (text) {  // 引数指定すると↑でreturnしたオブジェクトが入る（thenでチェーンしていける）
            // 加工や表示などの処理
            copyTextToClipboard(text)
        });
}

function connecttext(textid, ischecked) {
    if (ischecked == true) {
        // チェックが入っていたら有効化
        document.getElementById(textid).disabled = false;
    }
    else {
        // チェックが入っていなかったら無効化
        document.getElementById(textid).disabled = true;
    }
}
