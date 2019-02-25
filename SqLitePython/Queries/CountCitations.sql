SELECT citations.apmid as CitingPmid, a1.title as CitingTitle, a1.keywords as CitingKeywords, a1.pubyear as CitingPubyear, a1.jid as CitingJid,
a2.pmid as CitedPmid, a2.title as CitedTitle, a2.keywords as CitedKeywords, a2.pubyear as CitedPubyear, a2.jid as CitedJid
from citations 
INNER JOIN articles as a1 on a1.pmid = citations.apmid
INNER JOIN articles as a2 on a2.pmid = citations.bpmid