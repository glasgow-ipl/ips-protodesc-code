Improving Protocol Standards for a more Trustworthy Internet
============================================================

Colin Perkins  
Stephen McQuistin


## Summary

This project will make the Internet's infrastructure and applications more
reliable and secure, more trustworthy and less vulnerable to cyber attack,
by improving the engineering processes by which the network is designed.

The Internet comprises a large number of laptops, smartphones, and other
edge devices, connecting to servers located in data centres around the
world via numerous interconnecting links and switching devices. To make
this work, all the devices must agree on how they should communicate. That
is, they must speak a common language, known as a "protocol" that describes
the format of the information that is sent and the operations to be
performed. There are many such protocols, describing the different types 
of communication. For example, the HTTP protocol describes how browsers
fetch pages from websites.

To ensure interoperability between devices from different manufacturers,
these protocols are described in a series of standards documents, published
by organisations such as the Internet Engineering Task Force (IETF). These
standards are developed incrementally by teams of engineers working over
several months, or perhaps years, to produce a written specification that
describes how the protocol should work. Despite the best efforts of those
developing the standards, however, the results are often found to contain
inconsistencies and ambiguities. These can lead to devices from different
manufacturers failing to work together, due to differing interpretations of
the standard, and in the worst cases can lead to vulnerabilities that open
devices up to cyber attack.

Much of the reason for these inconsistencies and ambiguities is that the
protocol standards are written in English, and hence there's no automated
way of checking them for correctness. Researchers have proposed ways of
describing protocols using methods (known as "formal languages") that are
more like computer programming languages, and that would allow automated
consistency checks to be made, but these have not been widely adopted by
the standards community. 

This project will study the social, cultural, and educational barriers to
adoption of these new techniques, to understand why standards continue to
be written in English. We will explore the perceived limitations of the
alternatives, to understand why they've been adopted in certain niches, 
and for certain purposes, but are not used more broadly in standards
development.

We'll then formulate a model for the adoption of formal languages and their
supporting tools in the protocol standards community, and use it identify
areas that are ready to increase use of such techniques in their standards.
Finally, we'll use the knowledge gained to propose formal languages, that
are designed to fit the way the standards developers work, and begin the
process of introducing these into the standards process, to improve
protocol specifications and make them less vulnerable to attack.

The work will be conduced in the IETF, since it's the key international
technical standards body developing Internet protocol standards. The aim is
to improve the quality and trustworthiness of the standards that the IETF
develops, and increase security, robustness, and interoperability of the
Internet. The novel engineering research idea we will explore is that
formal languages need to be adapted to the community of interest. It is not
enough that they help solve the technical problem of how to specify a
protocol: they must do so in a way that fits the expertise and culture of
those who need to use them. Research into structured approaches and formal
languages for protocol design has not yet considered the nature of the
standards process, and hence has not seen wide uptake. We start with a deep
awareness of the standards process, consider social and technical barriers
to uptake, and propose new techniques to improve the way standards are
developed. 


## Acknowledgements

This work is funded by the UK Engineering and Physical Sciences Research
Council, under grant EP/R04144X/1.
