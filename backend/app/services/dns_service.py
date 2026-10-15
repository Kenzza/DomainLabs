import dns.resolver
import dns.exception
from typing import Dict, Any, List

def fetch_dns_intelligence(hostname: str) -> Dict[str, Any]:
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]
    records_data = {}
    
    has_any_success = False
    has_timeout = False
    has_failed = False
    all_not_found = True

    for rdtype in record_types:
        try:
            answers = dns.resolver.resolve(hostname, rdtype)
            ttl = answers.rrset.ttl if answers.rrset else 300
            items = []
            for rdata in answers:
                if rdtype == "MX":
                    items.append({
                        "value": str(rdata.exchange).rstrip('.'),
                        "preference": rdata.preference,
                        "ttl": ttl
                    })
                elif rdtype == "TXT":
                    txt_val = "".join([b.decode("utf-8", errors="ignore") if isinstance(b, bytes) else str(b) for b in rdata.strings])
                    items.append({
                        "value": txt_val,
                        "ttl": ttl
                    })
                else:
                    items.append({
                        "value": str(rdata).rstrip('.'),
                        "ttl": ttl
                    })
            
            records_data[rdtype] = {
                "status": "success",
                "items": items,
                "message": None
            }
            has_any_success = True
            all_not_found = False

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN):
            records_data[rdtype] = {
                "status": "not_found",
                "items": [],
                "message": f"No {rdtype} records found."
            }
        except dns.exception.Timeout:
            records_data[rdtype] = {
                "status": "timeout",
                "items": [],
                "message": f"DNS query for {rdtype} timed out."
            }
            has_timeout = True
            all_not_found = False
        except Exception as e:
            records_data[rdtype] = {
                "status": "failed",
                "items": [],
                "message": f"DNS query failed: {str(e)}"
            }
            has_failed = True
            all_not_found = False

    if has_any_success:
        overall_status = "success"
    elif has_timeout:
        overall_status = "timeout"
    elif has_failed:
        overall_status = "failed"
    else:
        overall_status = "not_found"

    return {
        "status": overall_status,
        "data": {
            "records": records_data
        },
        "message": None if has_any_success else "DNS lookup returned no records or failed."
    }
