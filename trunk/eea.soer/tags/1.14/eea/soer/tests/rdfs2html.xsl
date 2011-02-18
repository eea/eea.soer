<?xml version="1.0"?>
<?xml-stylesheet href="http://www.w3.org/StyleSheets/base.css" type="text/css"?>
<?xml-stylesheet href="http://www.w3.org/2002/02/style-xsl.css" type="text/css"?>
<?xml-stylesheet href="http://www.w3.org/2002/07/01-style-xsl.xsl" type="application/xml"?>
<!DOCTYPE xsl:stylesheet [
  <!ENTITY rdfnsuri "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <!ENTITY rdfsnsuri "http://www.w3.org/2000/01/rdf-schema#">
]>
  <xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0"
    xmlns="http://www.w3.org/1999/xhtml"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:ont="http://www.daml.org/2001/03/daml+oil#"
    xmlns:rdf="&rdfnsuri;"
    xmlns:rdfs="&rdfsnsuri;"
    xmlns:rcs="http://www.w3.org/2001/03swell/rcs#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    exclude-result-prefixes="dc ont rdf rdfs rcs r2h owl"
    xmlns:r2h='http://www.w3.org/2002/06/rdfs2html.xsl'>

  <xsl:output method="xml" indent='yes' doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <xsl:param name="recursive" select="'no'"/>
  <xsl:variable name="ns" select="/rdf:RDF/rdf:Description/@rdf:about"/>

  <html>
    <head>
    <title>RDF Schema formatter</title>
    <link rel="stylesheet" href="/StyleSheets/base.css" type="text/css"/>
    </head>
    <body>
    <p><a href="/"><img src="/Icons/w3c_home" alt="W3C"/></a></p>
    <h1>RDF Schema formatter</h1>
    <p>This XSLT extracts human readable information from a RDF Schema ; see <a href="http://www.w3.org/2000/06/webdata/xslt?xmlfile=http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns&amp;xslfile=http%3A%2F%2Fdev.w3.org%2Fcvsweb%2F%7Echeckout%7E%2F2004%2Frdfs2html%2Frdfs2html.xsl%3Frev%3D1.1">it applied</a> to the <a href="http://www.w3.org/1999/02/rdf-syntax-ns">RDF Syntax namespace</a>.</p>
    <p>Its casual use is to be linked to the RDF Schema with the XML PI <code>&lt;?xml-stylesheet href="<a href="http://www.w3.org/2002/06/rdfs2html.xsl">http://www.w3.org/2002/06/rdfs2html.xsl</a>" type="application/xml"?&gt;</code></p>
    <p>You can try and see its effects through the <a href="http://www.w3.org/2001/05/xslt">W3C XSLT online service</a>:</p>
    <form action="http://www.w3.org/2000/06/webdata/xslt" method="GET">
      <label>URI of the RDF Schema: <input type="text" name="xmlfile"/></label>
      <input type="hidden" name="xslfile" value="http://dev.w3.org/cvsweb/~checkout~/2004/rdfs2html/rdfs2html.xsl?rev=1.1"/>
      <input type="submit" value="Transform"/>
    </form>
    <p>Note that the on-line form uses an old version of the XSLT formatter, due to limitations of the XSLT servlet (e.g. support of the <code>namespace</code> XPath axis).</p>
    <p>Tip: if you generate your RDF Schema from an N3 version using a Makefile and <a href="http://www.w3.org/2000/10/swap/doc/cwm">CWM</a>, you can add automatically this XSLT as a styler with:<code>(echo "&lt;?xml-stylesheet href='/2002/06/rdfs2html' type='application/xml'?&gt;" &amp;&amp;<var>$(PYTHON)</var> <var>$(CWM)</var> <var>schema.n3</var> --rdf) &gt;<var>schema.rdf</var></code></p>
    <p class="copyright">Copyright &#169; 1994-2004 <a href="http://www.w3.org/">World Wide Web Consortium</a>, (<a
href="http://www.csail.mit.edu/"><abbr title="Massachusetts Institute of
Technology">M.I.T.</abbr></a>, <a
href="http://www.ercim.org/"><acronym
title="European Research Consortium for Informatics and Mathematics">ERCIM</acronym></a>, <a
href="http://www.keio.ac.jp/">Keio University</a>). All Rights
    Reserved. http://www.w3.org/Consortium/Legal/. W3C <a href="http://www.w3.org/Consortium/Legal/copyright-software">software licensing</a> rules apply.</p>
    <address>Created by <a href="http://www.w3.org/People/Dom/">Dominique Haza&#235;l-Massieux</a>, developed with contributions from others (see esp. the <a href="http://dev.w3.org/cvsweb/2004/rdfs2html/rdfs2html.xsl">version in W3C Public CVS server</a>) - $Id: rdfs2html.xsl,v 1.4 2004/03/23 09:13:26 dom Exp $</address>
    </body>
  </html>

  <xsl:template match="/">
    <xsl:variable name="schemacount" select="count(/rdf:RDF/*[@rdf:about]/dc:title | /rdf:RDF/*[@rdf:about and @dc:title])"/>
    <xsl:variable name="title">
      <xsl:choose>
        <xsl:when test="$schemacount=1">
          <xsl:choose>
            <xsl:when test="//*[@rdf:about='']/dc:title">
              <xsl:value-of select="//*[@rdf:about='']/dc:title"/>
            </xsl:when>
            <xsl:when test="//rdf:Description[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:title">
              <xsl:value-of select="//rdf:Description[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:title"/>
            </xsl:when>
            <xsl:when test="//owl:Ontology[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:title">
              <xsl:value-of select="//owl:Ontology[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:title"/>
            </xsl:when>
            <xsl:when test="//rdf:Description[@rdf:about]/dc:title">
              <xsl:value-of select="//rdf:Description[@rdf:about]/dc:title"/>
            </xsl:when>
            <xsl:when test="//*[@rdf:about and @dc:title]">
              <xsl:value-of select="//*/@dc:title"/>
            </xsl:when>
            <xsl:otherwise>
              Untitled RDF Schema
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          Multiple Schemas
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="description">
      <xsl:choose>
        <xsl:when test="$schemacount=1">
          <xsl:choose>
           <xsl:when test=".//*[@rdf:about='']/dc:description">
            <xsl:value-of select=".//*[@rdf:about='']/dc:description"/>
           </xsl:when>
           <xsl:when test=".//rdf:Description[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:description">
            <xsl:value-of select=".//rdf:Description[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:description"/>
           </xsl:when>
           <xsl:when test=".//owl:Ontology[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:description">
             <xsl:value-of select=".//owl:Ontology[@rdf:about and contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='']/dc:description"/>
           </xsl:when>
           <xsl:when test=".//rdf:Description[@rdf:about]/dc:description">
            <xsl:value-of select=".//rdf:Description[@rdf:about]/dc:description"/>
           </xsl:when>
           <xsl:when test=".//*[@rdf:about and @dc:title and @dc:description]">
            <xsl:value-of select=".//*/@dc:description"/>
           </xsl:when>
           <xsl:otherwise></xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          This document contains multiple schemas
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <html>
      <head>
        <title><xsl:value-of select="$title"/></title>
        <xsl:if test="normalize-space($description)">
          <meta name="description" content="{$description}"/>
        </xsl:if>
        <link rel="stylesheet" type="text/css" href="http://www.w3.org/StyleSheets/base.css"/>
        <link rel="stylesheet" type="text/css" href="http://www.w3.org/2002/07/01-rdf.css"/>
      </head>

      <body>
        <div id="header">
        <h1><xsl:value-of select="$title"/></h1>
        <xsl:choose>
          <xsl:when test="$schemacount=1">
            <xsl:if test="normalize-space($description)">
              <p><xsl:value-of select="$description"/></p>
            </xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="/rdf:RDF/*[@rdf:about]/dc:title"/>
          </xsl:otherwise>
        </xsl:choose>
        </div>
        <div id="note">
        <h4>Important note</h4>
        <p>You're reading an HTML formatting of an RDF Schema. Please note that the HTML view is only meant to be informational.  It is not complete.  Refer directly to the RDF Schema for the most complete information.  If you'd like to use this to present your own RDF Schema as HTML, see <a href="http://www.w3.org/2002/06/rdfs2html.xsl">the stylesheet</a>.</p>
        </div>
        <div id="content">
        <p><a href="#schemaProperties">Properties</a> | <a href="#schemaClasses">Classes</a> | <a href="#schemaUndetermined">Undetermined</a></p>
        <a name="schemaProperties" id="schemaProperties"></a>
        <xsl:variable name="propertycount" select="count(.//*[rdf:type/@rdf:resource='&rdfnsuri;Property' or (local-name()='Property' and namespace-uri()='&rdfnsuri;') or rdf:type/@rdf:resource='&rdfsnsuri;ConstraintProperty' or (local-name()='ConstraintProperty' and namespace-uri()='&rdfsnsuri;') or rdfs:subPropertyOf or rdfs:domain or rdfs:range])"/>
        <h2>Properties (<xsl:value-of select="$propertycount"/>)</h2>
        <xsl:if test="$propertycount!=0">
        <dl>
          <xsl:apply-templates select=".//*[rdf:type/@rdf:resource='&rdfnsuri;Property' or (local-name()='Property' and namespace-uri()='&rdfnsuri;') or rdf:type/@rdf:resource='&rdfsnsuri;ConstraintProperty' or (local-name()='ConstraintProperty' and namespace-uri()='&rdfsnsuri;') or rdfs:subPropertyOf or rdfs:domain or rdfs:range]" mode="details">
            <xsl:sort select="@rdf:about"/>
          </xsl:apply-templates>
        </dl>
        </xsl:if>
        <a name="schemaClasses" id="schemaClasses"></a>
        <xsl:variable name="classcount" select="count(.//*[rdf:type/@rdf:resource='&rdfsnsuri;Class' or (local-name()='Class' and namespace-uri()='&rdfsnsuri;') or rdfs:subClassOf])"/>
        <h2>Classes (<xsl:value-of select="$classcount"/>)</h2>
        <xsl:if test="$classcount!=0">
        <dl>
          <xsl:apply-templates select=".//*[rdf:type/@rdf:resource='&rdfsnsuri;Class' or (local-name()='Class' and namespace-uri()='&rdfsnsuri;') or rdfs:subClassOf]" mode="details">
            <xsl:sort select="@rdf:about"/>
          </xsl:apply-templates>
        </dl>
        </xsl:if>
        <a name="schemaUndetermined" id="schemaUndetermined"></a>
        <xsl:variable name="undeterminedcount" select="count(.//*[not(rdf:type/@rdf:resource='&rdfnsuri;Property' or (local-name()='Property' and namespace-uri()='&rdfnsuri;') or rdf:type/@rdf:resource='&rdfsnsuri;ConstraintProperty' or (local-name()='ConstraintProperty' and namespace-uri()='&rdfsnsuri;') or rdfs:subPropertyOf or rdfs:domain or rdfs:range) and not(rdf:type/@rdf:resource='&rdfsnsuri;Class' or (local-name()='Class' and namespace-uri()='&rdfsnsuri;') or rdfs:subClassOf) and not(local-name()='Description' and namespace-uri()='&rdfnsuri;' and (@rdf:about='' or (contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='')))][@rdf:about])"/>
        <h2>Undetermined (<xsl:value-of select="$undeterminedcount"/>)</h2>
        <xsl:if test="$undeterminedcount!=0">
        <dl>
          <xsl:apply-templates select=".//*[not(rdf:type/@rdf:resource='&rdfnsuri;Property' or (local-name()='Property' and namespace-uri()='&rdfnsuri;') or rdf:type/@rdf:resource='&rdfsnsuri;ConstraintProperty' or (local-name()='ConstraintProperty' and namespace-uri()='&rdfsnsuri;') or rdfs:subPropertyOf or rdfs:domain or rdfs:range) and not(rdf:type/@rdf:resource='&rdfsnsuri;Class' or (local-name()='Class' and namespace-uri()='&rdfsnsuri;') or rdfs:subClassOf) and not(local-name()='Description' and namespace-uri()='&rdfnsuri;' and  (@rdf:about='' or (contains(@rdf:about,'#') and substring-after(@rdf:about,'#')='')))][@rdf:about]" mode="details">
          <xsl:sort select="@rdf:about"/>
          </xsl:apply-templates>
        </dl>
        </xsl:if>
        </div>
        <h2>References</h2>
        <ul>
          <li><a href="http://www.w3.org/TR/REC-rdf-syntax/">RDF Syntax and Model</a></li>
          <li><a href="http://www.w3.org/TR/rdf-schema/">RDF Schemas</a></li>
          <!--          <li><a href="@@@">RDF Schema Validator</a></li>-->
        </ul>
        <hr/>
        <address>
          <xsl:value-of select=".//*[@rdf:about='']/rcs:id"/> (HTML display done through <a href="http://www.w3.org/2002/06/rdfs2html.xsl">http://www.w3.org/2002/06/rdfs2html.xsl</a> $Id: rdfs2html.xsl,v 1.4 2004/03/23 09:13:26 dom Exp $)
        </address>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="*" mode="details">
   <xsl:if test="@rdf:ID or @ID or @rdf:about or @about">
     <xsl:variable name="ref">
       <xsl:choose>
         <xsl:when test="@rdf:ID">
           <xsl:value-of select="concat('#',@rdf:ID)"/>
         </xsl:when>
         <xsl:when test="@rdf:about">
           <xsl:value-of select="@rdf:about"/>
         </xsl:when>
         <xsl:when test="@ID and namespace-uri()='&rdfnsuri;'">
           <xsl:value-of select="concat('#',@ID)"/>
         </xsl:when>
         <xsl:when test="@about  and namespace-uri()='&rdfnsuri;'">
           <xsl:value-of select="@about"/>
         </xsl:when>
       </xsl:choose>
     </xsl:variable>

     <dt>
      <span class="about">
      <xsl:call-template name="labelize">
        <xsl:with-param name="resource" select="$ref"/>
      </xsl:call-template>
      </span>
    </dt>
    <xsl:if test="rdfs:comment">
      <dd class="description"><pre><xsl:value-of select="rdfs:comment"/></pre></dd>
    </xsl:if>
    <xsl:apply-templates select="*[@rdf:resource]" mode="prop"/>
   </xsl:if>
  </xsl:template>


  <xsl:template match="*[@rdf:resource]" mode="prop">
    <dd>
      <xsl:choose>
        <xsl:when test="local-name()='type' and namespace-uri()='&rdfnsuri;'">
          <xsl:text>An instance of </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='seeAlso' and namespace-uri()='&rdfsnsuri;'">          <xsl:text>See also </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='isDefinedBy' and namespace-uri()='&rdfsnsuri;'">          <xsl:text>Defined by </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='subPropertyOf' and namespace-uri()='&rdfsnsuri;'">
          <xsl:text>Sub property of </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='domain' and namespace-uri()='&rdfsnsuri;'">
          <xsl:text>Applies to </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='range' and namespace-uri()='&rdfsnsuri;'">
          <xsl:text>Range: </xsl:text>
        </xsl:when>
        <xsl:when test="local-name()='subClassOf' and namespace-uri()='&rdfsnsuri;'">
          <xsl:text>Sub class of </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="labelize">
            <xsl:with-param name="resource" select="concat(namespace-uri(),local-name())"/>
          </xsl:call-template>
          <xsl:text> </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:call-template name="labelize"><xsl:with-param name="resource" select='@rdf:resource'/></xsl:call-template>
    </dd>
  </xsl:template>

  <xsl:template name="labelize">
    <xsl:param name="resource"/>

    <xsl:variable name="qname">
      <xsl:call-template name="create-qname">
        <xsl:with-param name="resource"><xsl:value-of select="$resource"/></xsl:with-param>
      </xsl:call-template>
    </xsl:variable>

    <xsl:choose>
      <!-- Testing if this is a URI relative to the current doc, an HTTP URI, or something else -->
      <xsl:when test="starts-with($resource,'#')">
        <xsl:choose>
          <xsl:when test="/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;') or (@about=$resource and namespace-uri()='&rdfnsuri;')]/rdfs:label">
            <xsl:value-of select="/rdf:RDF/*[@rdf:about=$resource  or @rdf:ID=substring-after($resource,'#') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;') or (@about=$resource and namespace-uri()='&rdfnsuri;')]/rdfs:label"/>
          </xsl:when>
          <xsl:otherwise>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="starts-with($resource,'http://') and
              /rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')]/rdfs:label">
            <xsl:choose>
              <!-- This test doesn't handle the case where the resouce doesn't use #-->
              <xsl:when test="/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')]/rdfs:label">
                <xsl:value-of select="/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')]/rdfs:label[1]"/>
              </xsl:when>
              <xsl:otherwise>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="starts-with($resource,'http://') and contains($resource,'#') and concat(substring-before($resource,'#'),'#')=$ns and /rdf:RDF/*[@rdf:about=$resource or @about=$resource]/rdfs:label">
            <xsl:value-of select="/rdf:RDF/*[@rdf:about=$resource or @about=$resource]/rdfs:label"/>
            <xsl:value-of select="$qname"/>
          </xsl:when>
          <xsl:when test="starts-with($resource,'http://') and $recursive='yes'">
            <xsl:message>
              Trying to read <xsl:value-of select="$resource"/>...
            <xsl:value-of select="name(document($resource)/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')])"/>
            </xsl:message>
            <xsl:choose>
              <!-- This test doesn't handle the case where the resouce doesn't use #-->
              <xsl:when test="document($resource)/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')]/rdfs:label">
                <xsl:value-of select="document($resource)/rdf:RDF/*[@rdf:about=$resource or @rdf:ID=substring-after($resource,'#') or (@about=$resource and namespace-uri()='&rdfnsuri;') or (@ID=substring-after($resource,'#') and namespace-uri()='&rdfnsuri;')]/rdfs:label[1]"/>
              </xsl:when>
              <xsl:otherwise>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:when test="string-length($resource)=0">
            <xsl:text>this schema</xsl:text>
          </xsl:when>
          <xsl:otherwise>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="$resource!='' and $qname!=''"> <!-- bc handle sick cases like log.n3->log.rdfs -->
      [<a href="{$resource}"><xsl:value-of select="$qname"/></a>]
    </xsl:if>
  </xsl:template>

  <xsl:template name="get-name">
    <xsl:param name="head"/>

    <xsl:choose>

      <xsl:when test="contains($head, '#')">

        <xsl:value-of select="substring-after($head, '#')"/>

      </xsl:when>

      <xsl:otherwise>

        <xsl:variable name="tail">
          <xsl:if test="contains($head, '/')">
            <xsl:value-of select="substring-after($head, '/')"/>
          </xsl:if>
        </xsl:variable> 

        <xsl:choose>
          <xsl:when test="$tail!=''">
            <xsl:call-template name="get-name">
              <xsl:with-param name="head">
                <xsl:value-of select="$tail"/>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$head"/>
          </xsl:otherwise>
        </xsl:choose>

      </xsl:otherwise>

    </xsl:choose>

  </xsl:template>

  <xsl:template name="get-namespace">
    <xsl:param name="uri"/>

    <xsl:variable name="name">
      <xsl:call-template name="get-name">
        <xsl:with-param name="head">
          <xsl:value-of select="$uri"/>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:variable>

    <xsl:value-of select="substring-before($uri, $name)"/>
  </xsl:template>

  <xsl:template name="get-prefix">
    <xsl:param name="uri"/>

    <xsl:variable name="namespace">
       <xsl:call-template name="get-namespace">
         <xsl:with-param name="uri">
           <xsl:value-of select="$uri"/>
         </xsl:with-param>
       </xsl:call-template>
     </xsl:variable>

     <xsl:for-each select="/rdf:RDF/namespace::*">
       <xsl:if test=".=$namespace">
         <xsl:value-of select="name()"/>
       </xsl:if>
     </xsl:for-each>

  </xsl:template>

  <xsl:template name="create-qname">
    <xsl:param name="resource"/>

     <xsl:variable name="name">
       <xsl:call-template name="get-name">
         <xsl:with-param name="head">
           <xsl:value-of select="$resource"/>
         </xsl:with-param>
       </xsl:call-template>
     </xsl:variable>

     <xsl:variable name="namespace">
       <xsl:call-template name="get-namespace">
         <xsl:with-param name="uri">
           <xsl:value-of select="$resource"/>
         </xsl:with-param>
       </xsl:call-template>
     </xsl:variable>

     <xsl:variable name="prefix">
       <xsl:call-template name="get-prefix">
         <xsl:with-param name="uri">
           <xsl:value-of select="$resource"/>
         </xsl:with-param>
       </xsl:call-template>
     </xsl:variable>

    <xsl:choose>
      <xsl:when test="$prefix!='' and $name!=''">
        <xsl:value-of select="$prefix"/>:<xsl:value-of select="$name"/>
      </xsl:when>
      <xsl:when test="$namespace!='' and $name!=''">
        <xsl:value-of select="$namespace"/><xsl:value-of select="$name"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$resource"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="dc:title">
    <xsl:if test="parent::rdf:Description or parent::owl:Ontology">
      <h2><xsl:value-of select="."/></h2>
      <p><xsl:value-of select="../dc:description"/></p>
    </xsl:if>
  </xsl:template>
 

</xsl:stylesheet>
