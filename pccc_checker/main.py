import requests
import xml.etree.ElementTree as ET

class PCCCValidator:
    def __init__(self, api_key: str):
        """
        관세청 UNI-PASS API 키를 사용하여 초기화합니다.
        """
        self.api_key = api_key
        self.url = "https://unipass.customs.go.kr:38010/ext/rest/persEcmQry/retrievePersEcm"

    def validate(self, pccc: str, name: str, phone: str) -> dict:
        """
        개인통관고유부호의 유효성을 검사합니다.
        phone: '01012345678' 형식 (하이픈 제외 권장)
        """
        params = {
            "crkyCn": self.api_key,
            "persEcm": pccc,
            "pltxNm": name,
            "cphoneNo": phone
        }

        try:
            # HTTPS 강제 및 타임아웃 설정
            response = requests.get(self.url, params=params, timeout=10)
            response.raise_for_status()
            
            return self._parse_xml(response.text)
        except Exception as e:
            return {"success": False, "message": f"Connection Error: {str(e)}"}

    def _parse_xml(self, xml_data: str) -> dict:
        """
        XML 응답을 파싱하여 결과 반환 (로그 기록 방지를 위해 데이터 가공)
        """
        root = ET.fromstring(xml_data)
        
        # tCnt가 1이면 일치, 0이면 불일치
        t_cnt = root.findtext(".//tCnt")
        
        if t_cnt == "1":
            return {"success": True, "message": "인증 성공: 정보가 일치합니다."}
        else:
            # 상세 에러 메시지 추출
            error_msg = root.findtext(".//rsltMsg") or "정보가 일치하지 않습니다."
            return {"success": False, "message": error_msg}