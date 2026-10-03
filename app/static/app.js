const state = { options: null, marketInfo: null, language: localStorage.getItem("fairvalue-language") || "en" };

const copy = {
  en: {
    navValuation:"Valuation",navMethod:"How it works",navAbout:"About",statusChecking:"Checking service",statusOnline:"Pricing online",statusUnavailable:"Service unavailable",
    eyebrow:"MARKET PRICE INTELLIGENCE",heroTitle:"Know the market.",heroAccent:"Price with confidence.",heroBody:"A market-informed valuation for Japanese used cars, built from more than 100,000 listings and presented with an expected price range.",metricListings:"market listings",metricCoverage:"range coverage",metricSpeed:"instant estimate",marketStatus:"MARKET STATUS",marketLive:"Live pricing",marketYear:"MARKET YEAR",
    vehicleProfile:"01 / VEHICLE PROFILE",tellUs:"Tell us about the car",requiredHint:"Required details are marked with an asterisk. More information improves the estimate.",identity:"Identity",manufacturer:"Manufacturer",model:"Model",selectManufacturer:"Select manufacturer",selectManufacturerFirst:"Select manufacturer first",selectModel:"Select model",noModels:"No models available",selectYear:"Select registration year",trim:"Grade / trim",selectTrim:"Select grade / trim",selectYearFirst:"Select registration year first",selectTrimFirst:"Select grade / trim first",selectFuel:"Select fuel",selectTransmission:"Select transmission",selectDrivetrain:"Select drivetrain",ageUsage:"Age & usage",registrationYear:"Registration year",mileage:"Mileage",configuration:"Configuration",fuel:"Fuel",transmission:"Transmission",drivetrain:"Drivetrain",prefecture:"Prefecture",repairHistory:"Repair history",notSpecified:"Not specified",unknown:"Unknown",noneReported:"None reported",reported:"Reported",privacy:"Your vehicle details are used only for this estimate.",calculate:"Calculate fair value",calculating:"Calculating…",
    valuationHere:"Your valuation will appear here",completeProfile:"Complete the vehicle profile to calculate a market-informed estimate.",fairPrice:"Fair advertised price",expectedRange:"Expected market range",marketContext:"Market confidence context",readingMarket:"Reading the market",comparing:"Comparing vehicle attributes against recent listings…",estimatedValue:"ESTIMATED FAIR VALUE",rangeBadge:"80% RANGE",advertisedPrice:"Estimated advertised vehicle price",expectedRangeUpper:"EXPECTED RANGE",guidance:"Market guidance",guidanceBody:"Condition, options, dealer fees and local demand may change the final selling price.",startAnother:"Start another valuation",couldNotCalculate:"We couldn't calculate that estimate",reviewDetails:"Review details",loadError:"Vehicle options could not be loaded. Refresh the page and try again.",optionsOutdated:"The vehicle options are out of date. Publish the latest ui_options.json and restart the service.",serviceConnectionError:"The pricing service is offline. Start the local API or check the deployed service.",valuationError:"The valuation request could not be completed.",
    methodology:"02 / METHODOLOGY",clearerDecision:"From market data to a clearer decision.",methodBody:"Our pricing engine evaluates the signals that shape advertised prices across Japan, then returns a central estimate and expected range.",describeVehicle:"Describe the vehicle",describeBody:"Manufacturer, model, age, mileage and configuration form the valuation profile.",comparePatterns:"Compare market patterns",compareBody:"Our valuation engine evaluates pricing relationships across the expanded market dataset.",understandRange:"Understand the range",rangeBody:"The expected interval expresses real market variation around the fair-price estimate.",footerText:"Clearer decisions for the Japanese used-car market.",getValuation:"Get a valuation",ourMethod:"Our method"
  },
  ja: {
    navValuation:"価格査定",navMethod:"査定の仕組み",navAbout:"サービス概要",statusChecking:"サービス確認中",statusOnline:"査定サービス稼働中",statusUnavailable:"サービス停止中",
    eyebrow:"中古車市場価格インテリジェンス",heroTitle:"相場を知り、",heroAccent:"納得の価格判断を。",heroBody:"10万件以上の中古車掲載データをもとに、適正価格と想定価格帯をすばやく算出します。",metricListings:"掲載車両データ",metricCoverage:"価格帯カバー率",metricSpeed:"スピード査定",marketStatus:"市場データ",marketLive:"リアルタイム査定",marketYear:"基準年",
    vehicleProfile:"01 / 車両情報",tellUs:"お車の情報を入力してください",requiredHint:"必須項目にはアスタリスクが付いています。詳しい情報ほど査定の参考になります。",identity:"車種情報",manufacturer:"メーカー",model:"車種",selectManufacturer:"メーカーを選択",selectManufacturerFirst:"先にメーカーを選択",selectModel:"車種を選択",noModels:"車種がありません",selectYear:"初度登録年を選択",trim:"グレード",selectTrim:"グレードを選択",selectYearFirst:"先に初度登録年を選択",selectTrimFirst:"先にグレードを選択",selectFuel:"燃料を選択",selectTransmission:"トランスミッションを選択",selectDrivetrain:"駆動方式を選択",ageUsage:"年式・走行距離",registrationYear:"初度登録年",mileage:"走行距離",configuration:"車両仕様",fuel:"燃料",transmission:"トランスミッション",drivetrain:"駆動方式",prefecture:"都道府県",repairHistory:"修復歴",notSpecified:"指定なし",unknown:"不明",noneReported:"修復歴なし",reported:"修復歴あり",privacy:"入力された車両情報は、この査定にのみ使用されます。",calculate:"適正価格を査定する",calculating:"査定中…",
    valuationHere:"査定結果がここに表示されます",completeProfile:"車両情報を入力すると、市場データに基づく査定価格を確認できます。",fairPrice:"適正な掲載価格",expectedRange:"想定価格帯",marketContext:"市場に基づく価格情報",readingMarket:"市場データを分析中",comparing:"車両情報と市場の掲載データを比較しています…",estimatedValue:"推定適正価格",rangeBadge:"80% 価格帯",advertisedPrice:"推定掲載車両価格",expectedRangeUpper:"想定価格帯",guidance:"価格について",guidanceBody:"車両状態、装備、販売店手数料、地域の需要により、実際の販売価格は変動します。",startAnother:"別の車両を査定する",couldNotCalculate:"査定価格を算出できませんでした",reviewDetails:"入力内容を確認",loadError:"選択肢を読み込めませんでした。ページを再読み込みしてください。",optionsOutdated:"車両選択データが古いため査定できません。最新の ui_options.json を公開してサービスを再起動してください。",serviceConnectionError:"査定サービスに接続できません。ローカルAPIまたは本番サービスを確認してください。",valuationError:"査定を完了できませんでした。",
    methodology:"02 / 査定の仕組み",clearerDecision:"市場データから、より明確な判断へ。",methodBody:"全国の中古車掲載価格に影響する要素を分析し、中心となる査定価格と想定価格帯を算出します。",describeVehicle:"車両情報を入力",describeBody:"メーカー、車種、年式、走行距離、仕様から査定条件を作成します。",comparePatterns:"市場価格を比較",compareBody:"豊富な掲載データから、車両条件ごとの価格傾向を分析します。",understandRange:"価格帯を確認",rangeBody:"査定価格を中心に、実際の市場で想定される価格の幅を表示します。",footerText:"日本の中古車選びに、より明確な価格判断を。",getValuation:"価格を査定",ourMethod:"査定の仕組み"
  }
};

const manufacturerEnglish = {
  "いすゞ":"Isuzu","アウディ":"Audi","アストンマーティン":"Aston Martin","アバルト":"Abarth","アルピーヌ":"Alpine","アルファ ロメオ":"Alfa Romeo","アルファロメオ":"Alfa Romeo","ウエストフィールド":"Westfield","オペル":"Opel","キャデラック":"Cadillac","クライスラー":"Chrysler","クライスラー・ジープ":"Jeep","ケータハム":"Caterham","シトロエン":"Citroën","シボレー":"Chevrolet","ジャガー":"Jaguar","ジープ":"Jeep","スズキ":"Suzuki","スバル":"Subaru","スマート":"Smart","ダイハツ":"Daihatsu","トヨタ":"Toyota","日産":"Nissan","ホンダ":"Honda","マツダ":"Mazda","三菱":"Mitsubishi","三菱ふそう":"Mitsubishi Fuso","レクサス":"Lexus","メルセデス・ベンツ":"Mercedes-Benz","メルセデスAMG":"Mercedes-AMG","フォルクスワーゲン":"Volkswagen","ボルボ":"Volvo","ポルシェ":"Porsche","プジョー":"Peugeot","ルノー":"Renault","フィアット":"Fiat","フェラーリ":"Ferrari","ランボルギーニ":"Lamborghini","ランドローバー":"Land Rover","マセラティ":"Maserati","ミニ":"MINI","光岡自動車":"Mitsuoka","日野自動車":"Hino","いすゞ自動車":"Isuzu"
};

const modelEnglish = {
  "アルファード":"Alphard","ヴェルファイア":"Vellfire","プリウス":"Prius","アクア":"Aqua","クラウン":"Crown","ハリアー":"Harrier","ランドクルーザー":"Land Cruiser","ランドクルーザープラド":"Land Cruiser Prado","ヤリス":"Yaris","カローラ":"Corolla","ノア":"Noah","ヴォクシー":"Voxy","シエンタ":"Sienta","ルーミー":"Roomy","ライズ":"Raize","ハイエース":"HiAce","セレナ":"Serena","ノート":"Note","エクストレイル":"X-Trail","デイズ":"Dayz","ルークス":"Roox","スカイライン":"Skyline","リーフ":"Leaf","フィット":"Fit","フリード":"Freed","ヴェゼル":"Vezel","ステップワゴン":"Step WGN","N-BOX":"N-BOX","ジムニー":"Jimny","ハスラー":"Hustler","スイフト":"Swift","スペーシア":"Spacia","ワゴンR":"Wagon R","フォレスター":"Forester","レヴォーグ":"Levorg","インプレッサ":"Impreza","アウトバック":"Outback","デリカD:5":"Delica D:5","アウトランダー":"Outlander","タント":"Tanto","ムーヴ":"Move","ミライース":"Mira e:S","CX-3":"CX-3","CX-5":"CX-5","CX-8":"CX-8","ロードスター":"Roadster"
};

const prefectureEnglish = {"北海道":"Hokkaido","青森県":"Aomori","岩手県":"Iwate","宮城県":"Miyagi","秋田県":"Akita","山形県":"Yamagata","福島県":"Fukushima","茨城県":"Ibaraki","栃木県":"Tochigi","群馬県":"Gunma","埼玉県":"Saitama","千葉県":"Chiba","東京都":"Tokyo","神奈川県":"Kanagawa","新潟県":"Niigata","富山県":"Toyama","石川県":"Ishikawa","福井県":"Fukui","山梨県":"Yamanashi","長野県":"Nagano","岐阜県":"Gifu","静岡県":"Shizuoka","愛知県":"Aichi","三重県":"Mie","滋賀県":"Shiga","京都府":"Kyoto","大阪府":"Osaka","兵庫県":"Hyogo","奈良県":"Nara","和歌山県":"Wakayama","鳥取県":"Tottori","島根県":"Shimane","岡山県":"Okayama","広島県":"Hiroshima","山口県":"Yamaguchi","徳島県":"Tokushima","香川県":"Kagawa","愛媛県":"Ehime","高知県":"Kochi","福岡県":"Fukuoka","佐賀県":"Saga","長崎県":"Nagasaki","熊本県":"Kumamoto","大分県":"Oita","宮崎県":"Miyazaki","鹿児島県":"Kagoshima","沖縄県":"Okinawa"};

const optionEnglish = {"プラグインハイブリッド":"Plug-in hybrid","電気自動車":"Electric vehicle","ディーゼル":"Diesel","ハイブリッド":"Hybrid","ガソリン":"Gasoline","軽油":"Diesel","電気":"Electric","水素":"Hydrogen","その他":"Other ","不明":"Unknown","オートマチック":"Automatic","オートマ":"Automatic","マニュアル":"Manual","無段変速":"CVT","インパネ":"Dashboard ","コラム":"Column ","フロア":"Floor ","MTモード付き":"manual mode ","MTモード付":"manual mode ","モード付き":"manual mode ","モード付":"manual mode ","速":"-speed","前輪駆動":"Front-wheel drive","後輪駆動":"Rear-wheel drive","四輪駆動":"Four-wheel drive"};

const $ = (selector) => document.querySelector(selector);
const form = $("#valuation-form");
const manufacturer = $("#manufacturer");
const model = $("#model");
const mileageInput = form.elements.mileage_km;
const mileageRange = $("#mileage-range");

const t = (key) => copy[state.language][key] || copy.en[key] || key;

function romanizeKana(value) {
  const pairs = {"キャ":"kya","キュ":"kyu","キョ":"kyo","シャ":"sha","シュ":"shu","ショ":"sho","チャ":"cha","チュ":"chu","チョ":"cho","ニャ":"nya","ニュ":"nyu","ニョ":"nyo","ヒャ":"hya","ヒュ":"hyu","ヒョ":"hyo","ミャ":"mya","ミュ":"myu","ミョ":"myo","リャ":"rya","リュ":"ryu","リョ":"ryo","ギャ":"gya","ギュ":"gyu","ギョ":"gyo","ジャ":"ja","ジュ":"ju","ジョ":"jo","ビャ":"bya","ビュ":"byu","ビョ":"byo","ピャ":"pya","ピュ":"pyu","ピョ":"pyo","ティ":"ti","ディ":"di","ファ":"fa","フィ":"fi","フェ":"fe","フォ":"fo","ウィ":"wi","ウェ":"we","ウォ":"wo","ヴァ":"va","ヴィ":"vi","ヴ":"vu","ヴェ":"ve","ヴォ":"vo"};
  const single = {"ア":"a","イ":"i","ウ":"u","エ":"e","オ":"o","カ":"ka","キ":"ki","ク":"ku","ケ":"ke","コ":"ko","サ":"sa","シ":"shi","ス":"su","セ":"se","ソ":"so","タ":"ta","チ":"chi","ツ":"tsu","テ":"te","ト":"to","ナ":"na","ニ":"ni","ヌ":"nu","ネ":"ne","ノ":"no","ハ":"ha","ヒ":"hi","フ":"fu","ヘ":"he","ホ":"ho","マ":"ma","ミ":"mi","ム":"mu","メ":"me","モ":"mo","ヤ":"ya","ユ":"yu","ヨ":"yo","ラ":"ra","リ":"ri","ル":"ru","レ":"re","ロ":"ro","ワ":"wa","ヲ":"o","ン":"n","ガ":"ga","ギ":"gi","グ":"gu","ゲ":"ge","ゴ":"go","ザ":"za","ジ":"ji","ズ":"zu","ゼ":"ze","ゾ":"zo","ダ":"da","ヂ":"ji","ヅ":"zu","デ":"de","ド":"do","バ":"ba","ビ":"bi","ブ":"bu","ベ":"be","ボ":"bo","パ":"pa","ピ":"pi","プ":"pu","ペ":"pe","ポ":"po","ー":"-"};
  let katakana = value.replace(/[ぁ-ゖ]/g, (char) => String.fromCharCode(char.charCodeAt(0) + 0x60));
  Object.entries(pairs).forEach(([key, result]) => { katakana = katakana.split(key).join(result); });
  let output = "";
  for (let index = 0; index < katakana.length; index += 1) {
    const char = katakana[index];
    if (char === "ッ") {
      const next = single[katakana[index + 1]] || "";
      output += next.charAt(0);
    } else if (char === "ー") {
      const vowel = [...output].reverse().find((letter) => "aeiou".includes(letter));
      output += vowel || "";
    } else {
      output += single[char] || char;
    }
  }
  return output.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function englishLabel(value, type) {
  if (type === "manufacturer") return manufacturerEnglish[value] || romanizeKana(value);
  if (type === "model") {
    const curated = state.options?.model_english_names?.[value] || modelEnglish[value];
    if (curated) return curated;
    const hasJapanese = /[\u3040-\u30ff\u4e00-\u9faf]/.test(value);
    return hasJapanese ? `${romanizeKana(value)} (${value})` : value;
  }
  if (type === "prefecture") return prefectureEnglish[value] || romanizeKana(value);
  if (optionEnglish[value]) return optionEnglish[value];
  let label = value;
  Object.entries(optionEnglish).forEach(([ja, en]) => { label = label.split(ja).join(en); });
  return romanizeKana(label);
}

function localizedLabel(value, type) {
  const displayValue = type === "model" ? (state.options?.model_display_names?.[value] || value) : value;
  return state.language === "ja" ? displayValue : englishLabel(displayValue, type);
}

function applyLanguage() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.classList.toggle("active", button.dataset.language === state.language);
  });
  if (state.options) renderOptionLists();
  const status = $("#api-status");
  if (status.classList.contains("ready")) status.querySelector("b").textContent = t("statusOnline");
}

function option(value, label = value) {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

function populateSelect(id, values, type, placeholder = t("notSpecified")) {
  const select = $(id);
  const current = select.value;
  select.replaceChildren(option("", placeholder));
  values.forEach((value) => select.append(option(value, localizedLabel(value, type))));
  if ([...select.options].some((item) => item.value === current)) select.value = current;
}

function populateDependentSelect(id, values, type, required = false, placeholderKey = "selectEarlierFields") {
  populateSelect(id, values, type, t(placeholderKey));
  const select = $(id);
  select.disabled = values.length === 0;
  select.required = required && values.length > 0;
  if (values.length === 1) select.value = values[0];
  return select.value;
}

function buildYears(referenceYear = new Date().getFullYear(), availableYears = null) {
  const yearSelect = $("#registration-year");
  const current = yearSelect.value;
  const years = availableYears || Array.from({ length: referenceYear - 1979 }, (_, index) => referenceYear - index);
  yearSelect.replaceChildren(option("", t("selectYear")));
  years.forEach((year) => {
    yearSelect.append(option(String(year), String(year)));
  });
  if (years.map(String).includes(current)) yearSelect.value = current;
  yearSelect.disabled = years.length === 0;
}

function selectedVehicleYears() {
  return state.options?.vehicle_options?.[manufacturer.value]?.[model.value] || null;
}

function updateConfigurationOptions() {
  const byYear = selectedVehicleYears();
  const configuration = byYear?.[$("#registration-year").value];
  const trims = configuration?.trim || [];
  const selectedTrim = populateDependentSelect("#trim", trims, "option", true, configuration ? "selectTrim" : "selectYearFirst");
  $("#trim-required-marker").hidden = trims.length === 0;
  const trimConfiguration = trims.length
    ? configuration?.trim_options?.[selectedTrim]
    : configuration;
  const prerequisite = configuration && trims.length ? "selectTrimFirst" : "selectYearFirst";
  populateDependentSelect("#fuel", trimConfiguration?.fuel || [], "option", true, trimConfiguration ? "selectFuel" : prerequisite);
  populateDependentSelect("#transmission", trimConfiguration?.transmission || [], "option", true, trimConfiguration ? "selectTransmission" : prerequisite);
  populateDependentSelect("#drivetrain", trimConfiguration?.drivetrain || [], "option", true, trimConfiguration ? "selectDrivetrain" : prerequisite);
}

function updateYears() {
  const byYear = selectedVehicleYears();
  const years = byYear ? Object.keys(byYear).map(Number).sort((a, b) => b - a) : [];
  buildYears(state.marketInfo?.model_reference_year, years);
  updateConfigurationOptions();
}

function updateModels() {
  const models = state.options?.manufacturer_to_models?.[manufacturer.value] || [];
  const current = model.value;
  model.replaceChildren(option("", models.length ? t("selectModel") : t("noModels")));
  models.forEach((name) => model.append(option(name, localizedLabel(name, "model"))));
  if (models.includes(current)) model.value = current;
  model.disabled = models.length === 0;
  updateYears();
}

function renderOptionLists() {
  const selectedManufacturer = manufacturer.value;
  manufacturer.replaceChildren(option("", t("selectManufacturer")));
  Object.keys(state.options.manufacturer_to_models)
    .sort((a, b) => localizedLabel(a, "manufacturer").localeCompare(localizedLabel(b, "manufacturer"), state.language))
    .forEach((name) => manufacturer.append(option(name, localizedLabel(name, "manufacturer"))));
  if (state.options.manufacturer_to_models[selectedManufacturer]) manufacturer.value = selectedManufacturer;
  updateModels();
  updateConfigurationOptions();
  populateSelect("#prefecture", state.options.prefecture_values || [], "prefecture");
}

async function loadApplicationData() {
  const status = $("#api-status");
  try {
    const [healthResponse, optionsResponse, infoResponse] = await Promise.all([
      fetch("/health"), fetch("/v1/options"), fetch("/v1/model-info")
    ]);
    if (!healthResponse.ok || !optionsResponse.ok || !infoResponse.ok) throw new Error("Service metadata unavailable");
    const health = await healthResponse.json();
    state.options = await optionsResponse.json();
    state.marketInfo = await infoResponse.json();
    if (Number(state.options.schema_version || 0) < 3 || !state.options.vehicle_options) {
      throw new Error(t("optionsOutdated"));
    }
    renderOptionLists();
    updateYears();
    $("#reference-year").textContent = state.marketInfo.model_reference_year;
    status.classList.toggle("ready", health.status === "ok");
    status.querySelector("b").textContent = health.status === "ok" ? t("statusOnline") : t("statusChecking");
  } catch (error) {
    buildYears(new Date().getFullYear(), []);
    status.querySelector("b").textContent = t("statusUnavailable");
    showError(error.message || t("loadError"));
  }
}

function setPanel(panel) {
  ["#result-empty", "#result-loading", "#result-content", "#result-error"]
    .forEach((id) => { $(id).hidden = id !== panel; });
}

function showError(message) {
  $("#error-message").textContent = message;
  setPanel("#result-error");
}

function formatYen(value) {
  return new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY", maximumFractionDigits: 0 }).format(value);
}

function payloadFromForm() {
  const data = new FormData(form);
  const payload = {};
  for (const [key, rawValue] of data.entries()) {
    const value = typeof rawValue === "string" ? rawValue.trim() : rawValue;
    if (value === "") continue;
    payload[key] = value;
  }
  payload.registration_year = Number(payload.registration_year);
  payload.mileage_km = Number(payload.mileage_km);
  if (payload.repair_history !== undefined) payload.repair_history = payload.repair_history === "true";
  return payload;
}

function renderResult(result, payload) {
  $("#fair-price").textContent = formatYen(result.estimated_fair_price_jpy);
  $("#range-low").textContent = formatYen(result.expected_range_low_jpy);
  $("#range-high").textContent = formatYen(result.expected_range_high_jpy);
  const span = Math.max(1, result.expected_range_high_jpy - result.expected_range_low_jpy);
  const position = Math.min(90, Math.max(10, ((result.estimated_fair_price_jpy - result.expected_range_low_jpy) / span) * 100));
  $("#range-marker").style.left = `${position}%`;
  const summary = [localizedLabel(payload.manufacturer, "manufacturer"), localizedLabel(payload.model, "model"), `${payload.registration_year}`, `${Number(payload.mileage_km).toLocaleString()} km`, payload.fuel ? localizedLabel(payload.fuel, "option") : null].filter(Boolean);
  $("#vehicle-summary").replaceChildren(...summary.map((text) => { const chip = document.createElement("span"); chip.textContent = text; return chip; }));
  setPanel("#result-content");
}

async function fetchPrediction(payload) {
  let response;
  try {
    response = await fetch("/v1/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new Error(t("serviceConnectionError"));
  }
  const body = await response.json();
  if (!response.ok) throw new Error(state.language === "ja" ? t("valuationError") : (body?.error?.message || t("valuationError")));
  return body;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const button = $("#submit-button");
  button.disabled = true;
  button.querySelector("span").textContent = t("calculating");
  setPanel("#result-loading");
  $("#result-panel").scrollIntoView({ behavior: "smooth", block: "center" });
  try {
    const payload = payloadFromForm();
    renderResult(await fetchPrediction(payload), payload);
  } catch (error) {
    showError(error.message);
  } finally {
    button.disabled = false;
    button.querySelector("span").textContent = t("calculate");
  }
});

manufacturer.addEventListener("change", updateModels);
model.addEventListener("change", updateYears);
$("#registration-year").addEventListener("change", updateConfigurationOptions);
$("#trim").addEventListener("change", updateConfigurationOptions);
mileageRange.addEventListener("input", () => { mileageInput.value = mileageRange.value; });
mileageInput.addEventListener("input", () => { mileageRange.value = Math.min(250000, Number(mileageInput.value || 0)); });
$("#reset-button").addEventListener("click", () => { form.reset(); model.disabled = true; updateModels(); mileageRange.value = mileageInput.value; setPanel("#result-empty"); form.scrollIntoView({ behavior: "smooth" }); });
$("#retry-button").addEventListener("click", () => { setPanel("#result-empty"); form.scrollIntoView({ behavior: "smooth" }); });

document.querySelectorAll("[data-language]").forEach((button) => {
  button.addEventListener("click", () => {
    state.language = button.dataset.language;
    localStorage.setItem("fairvalue-language", state.language);
    applyLanguage();
  });
});

applyLanguage();
loadApplicationData();
