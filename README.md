# openrussian-to-yomitan
Yomitan-compatible dictionaries from OpenRussian data.

Additionally, a meta dictionary with A. A. Zaliznyak's classification for each word is shared here.

## Instructions
1. Download OpenRussian data from [here](https://app.togetherdb.com/db/fwoedz5fvtwvq03v/russian3).
2. Place the downloaded files in `russian3` folder.
3. Create an `opr` folder in the `dict` folder.
4. Run  the script (`jq` and `zip` required): 
```bash
chmod +x run.sh
./run.sh
```
# Attribution
* `generate_dict` and `utils.py` were originally shared by @Holence in the [OpenRussian_MDict](https://github.com/Holence/OpenRussian_MDict) repo (CC-BY-SA 4.0).
* Entry layout was originally created by @StefanVukovic99 in the [kaikki-to-yomitan](https://github.com/yomidevs/kaikki-to-yomitan) repo.
* OpenRussian.org data is licensed under CC-BY-SA.
* The data for A. A. Zaliznyak's dictionary was originally shared by @gramdict in the [zalizniak-2010](https://github.com/gramdict/zalizniak-2010) repo (CC BY-NC 4.0).