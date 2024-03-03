# DDMod_viewer
遊戲Darkest Dungeon的模組管理器

因原版模組排序太過難用，故自製一個管理器

參考了 robojumper 的 [ddsaveedit](https://github.com/robojumper/DarkestDungeonSaveEditor/tree/master/rust/ddsaveedit/wasm-ddsaveedit) 以了解檔案結構


### 目前能做到:

>1.解析遊戲加密文件

>2.網頁瀏覽遊戲文件

>3.模組依規則自行排序

>4.重新寫回檔案

使用方法為:

>1.選擇Steam的remote存檔資料夾
  
>2.選擇Steam的DarkestDungeon資料夾
  
>3.點擊 Check Game Saves確認路徑
  
>4.若路徑無誤，將顯示遊戲中的每個存檔
  
>5.至模組管理頁面查看模組
  
>6.自動排序後點選導出，將導出於程式資料夾下


將persist.game.json覆蓋回去之前請先備份，(之後可能用程式幫你備份好)

功能尚在完善，檔案丟失損毀恕不負責，
  
資料管理尚為Read Only，更動後寫回功能為待辦
  
尚有Bug待處理，多為gradio方面

![image](https://cdn.discordapp.com/attachments/804707001409601547/1213890746516504606/image.png?ex=65f71eda&is=65e4a9da&hm=b4c2d314e006a8d0b5037884ddaa892f98c49add6929e7fe0124c240585e11ac&)
![image](https://media.discordapp.net/attachments/804707001409601547/1213887429539536986/image.png?ex=65f71bc4&is=65e4a6c4&hm=0ea6d893e5964d370b77dd04bafde35918de310ca3b5e389ff36e4c76ea504c9&=&format=webp&quality=lossless&width=1190&height=660)
![image](https://media.discordapp.net/attachments/804707001409601547/1213887505707958302/image.png?ex=65f71bd6&is=65e4a6d6&hm=9cf3483b433c168550e15735d86445a95982bce6e9dd1b6b63dd3d6cfc0545c2&=&format=webp&quality=lossless&width=1440&height=633)
![image](https://cdn.discordapp.com/attachments/804707001409601547/1213898116080730112/image.png?ex=65f725b8&is=65e4b0b8&hm=4416a0389b4d566cfe7a9dcffe6008d30acd7698e389d418ab865cc5df537089&)
