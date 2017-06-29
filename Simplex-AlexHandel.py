#Trabalho de PL - implentacao do metodo simplex
#ALUNO: Alex Pungartnik Handel
#DRE: 114147792
#Periodo: 2017.1


import numpy

#funcao auxiliares da leitura
def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
    	print("INPUT MUST CONSIST OF INTEGERS")
        raise

def representsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
    	print("INPUT MUST CONSIST OF REAL NUMBERS")
        raise


#funcao que le as entradas
def readlines():
	coefficientList=[]
	#primeira linha: n e m
	linha1raw=str(raw_input(""))
	linha1temp=linha1raw.split(" ")
	if len(linha1temp)!=2:
		raise IOError("FIRST LINE MUST CONTAIN 2 INTEGERS")
	for number in linha1temp:
		representsInt(number)
	n=int(linha1temp[0])
	m=int(linha1temp[1])
	if n<=0 or n>50 or m<=0 or m>100:
		raise IOError("INPUT CONSTRAINTS EXCEEDED")
	#print("N: ", n, "M: ", m)
	#segunda linha
	linha2raw=str(raw_input(""))
	linha2temp=linha2raw.split(" ")
	problemType=linha2temp[0]
	for number in linha2temp[1::]:
		representsFloat(number)
		coefficientList.append(float(number))
	if len(linha2temp[1::])!=n:
		raise IOError("PLEASE INPUT EXACTLY AS MANY COEFFICIENTS AS YOU HAVE VARIABLES")
	if problemType!="min" and problemType!="max":
		raise IOError("PLEASE START THE 2ND LINE WITH MIN OR MAX")
	#print(problemType,coefficientList)
	#proximas linhas
	restrictionCoefficientMatrix=numpy.zeros((m,n))
	RHS=numpy.zeros((m,1))
	restrictionTypeList=[]
	for i in range (0,m):
		try:
			linhaR=str(raw_input(""))
		except EOFError:
			print("PLEASE TYPE M LINES")
			raise
		linhaRtemp=linhaR.split(" ")
		#print(i,linhaRtemp)
		for c in range(0,n):
			restrictionCoefficientMatrix[i][c]=float(linhaRtemp[c])
		restrictionTypeList.append(linhaRtemp[n])
		RHS[i][0]=linhaRtemp[n+1]
	#print(restrictionCoefficientMatrix)
	#print(restrictionTypeList)
	#print(RHS)
	#ultima linha
	varRestrictions=[]
	try:
		lastLineRaw=str(raw_input(""))
	except EOFError:
		print("INPUT ERROR")
		raise
	lastLineTemp=lastLineRaw.split(" ")
	for r in lastLineTemp:
		if r!="<" and r!=">" and r!="L":
			raise IOError("INPUT ERROR ON LAST LINE")
		varRestrictions.append(r)
	#print(varRestrictions)
	return n,m,problemType,coefficientList,restrictionCoefficientMatrix,restrictionTypeList,RHS,varRestrictions

#funcao que imprime uma tabela do simplex formatada como pedido
def printSimplexTable(ttable):
	for i in range(0,ttable.shape[0]):
		for j in range(0,ttable.shape[1]):
			print("%0.4f"%ttable[i][j]),
		print("")

#funcao que imprime um vertice formatado
def printVertex(vertex,i):
	print("V%d"%i),
	for e in vertex:
		print("%0.4f"%e),
	print("")

#funcao que faz a padronizacao do PPL
def padronize(n,m,problemType,coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions):
	#comeco do primeiro passo: variaveis tipo <
	newvarRestrictions=list(varRestrictions)
	newcoefficientList=list(coefficientList)
	newrestrictionCoefficientMatrix=restrictionCoefficientMatrix
	newrestrictionTypeList=list(restrictionTypeList)
	for i in range(0,n): 
		if varRestrictions[i]=="<":
			newvarRestrictions[i]=">"
			newcoefficientList[i]=coefficientList[i]*-1
			newrestrictionCoefficientMatrix[:,i]=restrictionCoefficientMatrix[:,i]*-1
	#segundo passo: variaveis irrestritas
	for i in range(0,n): 
		if varRestrictions[i]=="L":
			newvarRestrictions.insert(i+1,">")
			newvarRestrictions[i]=">"
			newcoefficientList.insert(i+1,coefficientList[i]*-1)
			z=restrictionCoefficientMatrix[:,i]*-1
			newrestrictionCoefficientMatrix=numpy.insert(newrestrictionCoefficientMatrix,i+1,values=z,axis=1)
	#terceiro passo: tipos das restricoes
	for i in range(0,m):
		if restrictionTypeList[i]!="=":
			newrestrictionTypeList[i]="="
			newvarRestrictions.insert(len(newvarRestrictions),">")
			newcoefficientList.insert(len(newcoefficientList),0)
			temp=numpy.zeros((m,1))
			if restrictionTypeList[i]==">":
				temp[i]=-1
			else:
				temp[i]=1
			newrestrictionCoefficientMatrix=numpy.append(newrestrictionCoefficientMatrix,temp,axis=1)	
	#quarto passo: max para min
	if problemType=="max":
		for x in range(0,len(newcoefficientList)):
			newcoefficientList[x]=newcoefficientList[x]*-1
	return newcoefficientList,newrestrictionCoefficientMatrix,newrestrictionTypeList,newvarRestrictions
	pass

#funcao que coloca as variaveis artificiais para comecar a fase 1
def AddArtificialVariable(n,m,coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions):
	for i in range(0,m):
		if restrictionTypeList[i]==">" or restrictionTypeList[i]=="=":
			coefficientList.insert(len(coefficientList),0)
			varRestrictions.insert(len(varRestrictions),">")
			temp=numpy.zeros((m,1))
			temp[i]=1
			restrictionCoefficientMatrix=numpy.append(restrictionCoefficientMatrix,temp,axis=1)
	for e in range(0,m): restrictionTypeList[e]="="
	return coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions

#funcao que acha o indice de uma variavel na lista das nao basicas
def findIndex(x,n,m,restrictionTypeList,coefficientList):
	nSlack=0
	nArtificial=0
	l=len(restrictionTypeList)
	for i in range(0,l):
		if restrictionTypeList[i]=="=":
			nArtificial+=1
		if restrictionTypeList[i]==">":
			nSlack+=1
			nArtificial+=1
		if restrictionTypeList[i]=="<":
			nSlack+=1
	nNormal=len(coefficientList)-nArtificial-nSlack
	index=nNormal+x-restrictionTypeList[:x].count("=")
	return index


#funcao que escolhe as variaveis basicas para comecar a fase 1
def pickBasicsPhase1(n,m,restrictionTypeList,coefficientList):
	Basics=[]
	nSlack=0
	nArtificial=0
	l=len(restrictionTypeList)
	for i in range(0,l):
		if restrictionTypeList[i]=="=":
			nArtificial+=1
		if restrictionTypeList[i]==">":
			nSlack+=1
			nArtificial+=1
		if restrictionTypeList[i]=="<":
			nSlack+=1
	nNormal=len(coefficientList)-nArtificial-nSlack
	for i in range(0,l):
		if restrictionTypeList[i]==">" or restrictionTypeList[i]=="=":
			Basics.insert(len(Basics),nNormal+nSlack+i-restrictionTypeList[:i].count("<"))
		elif restrictionTypeList[i]=="<":
			Basics.insert(len(Basics),findIndex(x=i,n=n,m=m,restrictionTypeList=list(restrictionTypeList),coefficientList=coefficientList))
	return Basics

#calcula a linha z para a fase 1, com a funcao objetivo artificial
def calculateZLine(oldZline,nA,baseList,table):
	newzline=oldZline.copy()
	artificialVariableIndexes=numpy.where(numpy.array(baseList)>=len(oldZline)-1-nA)[0]
	for i in artificialVariableIndexes:
		newzline=newzline+(-1*table[i])
	return newzline

#funcao que gera a primeira tabela da fase 1
def generateFirstTable(n,m,nA,baseList,coefficientList,restrictionCoefficientMatrix,RHS):
	table=restrictionCoefficientMatrix.copy()
	table=numpy.append(table,RHS,axis=1)
	zline=numpy.zeros(len(coefficientList)+1)
	for i in range(2,nA+2):
		zline[len(zline)-i]=1
	zline=calculateZLine(oldZline=zline,nA=nA,baseList=list(baseList),table=table.copy())
	table=numpy.insert(table,0,zline,axis=0)
	return table

#iteracao do Simplex,ate que se encontre uma tabela "otima"
def simplexStep(baseList,nBaseList,ttable,b):
	newTable=ttable.copy()
	nRows=ttable.shape[0]
	nCols=ttable.shape[1]
	if min(ttable[0][:len(ttable[0])-1])>=0:
		return baseList,nBaseList,ttable,False
	indexforIN=ttable[0].tolist().index(min(ttable[0][:len(ttable[0])-1]))
	r=[]
	for i in range(1,nRows):
		try:
			r.append(ttable[i][nCols-1]/ttable[i][indexforIN])
		except:
			continue
	if max(r)<0:
		return baseList,nBaseList,ttable,False

	indexforOUT=r.index(min(numpy.array([num for num in r if num >= 0])))
	pivot=ttable[indexforOUT+1,indexforIN]
	nBaseList[nBaseList.index(indexforIN)]=baseList[indexforOUT]
	baseList[indexforOUT]=indexforIN
	pivotLine=ttable[indexforOUT+1,:]/pivot
	ttable[indexforOUT+1,:]=pivotLine
	for i in range(0,nRows):
		if i==indexforOUT+1: 
			continue
		else:
			thisLine=ttable[i,:]
			coefficient=ttable[i,indexforIN]
			ttable[i,:]=thisLine-(pivotLine*coefficient)
	
	if min(ttable[0][:len(ttable[0])-1])>=0:
		return baseList,nBaseList,ttable,False	
	else:
		return baseList,nBaseList,ttable,True
	
#iteracao do Simplex caso ocorram multiplas ou infinitas solucoes
#NOTA: a funcao quando recebe o ftype=3 seria para caso de infinitas solucoes, porem essa parte acabou nao sendo implementada 
def modifiedSimplexStep(baseList,nBaseList,ttable,b,ftype):
	newTable=ttable.copy()
	nRows=ttable.shape[0]
	nCols=ttable.shape[1]
	for e in nBaseList:
		if ttable[0,e]<=0:
			indexforIN=e
			break
	r=[]
	for i in range(1,nRows):
		try:
			r.append(ttable[i][nCols-1]/ttable[i][indexforIN])
		except:
			continue
	if ftype==2:
		indexforOUT=r.index(min(numpy.array([num for num in r if num >= 0])))
	else:
		indexforOUT=r.index(min(r))
	pivot=ttable[indexforOUT+1,indexforIN]
	nBaseList[nBaseList.index(indexforIN)]=baseList[indexforOUT]
	baseList[indexforOUT]=indexforIN
	pivotLine=ttable[indexforOUT+1,:]/pivot
	ttable[indexforOUT+1,:]=pivotLine
	for i in range(0,nRows):
		if i==indexforOUT+1: 
			continue
		else:
			thisLine=ttable[i,:]
			coefficient=ttable[i,indexforIN]
			ttable[i,:]=thisLine-(pivotLine*coefficient)
	
	if min(ttable[0][:len(ttable[0])-1])>=0:
		return baseList,nBaseList,ttable	
	else:
		return baseList,nBaseList,ttable

#funcao que pega a tabela final da fase 1, tira as variaveis artificias e calcula a nova linha z
def makeTablePhase2(ttable,baseList,nBaseList,nArtificial,coefficientList,matrixA):
	count=0
	newBaseList=list(baseList)
	newNonBaseList=list(nBaseList)
	l=len(coefficientList)
	for i in range(0,nArtificial):
		matrixA=numpy.delete(matrixA,l-i-1,1)
		del coefficientList[l-i-1]
		newNonBaseList.remove(l-i-1)
		ttable=numpy.delete(ttable,l-i-1,1)
	nRows=ttable.shape[0]
	nCols=ttable.shape[1]
	matrixN=numpy.zeros((nRows-1,len(newNonBaseList)))
	matrixB=numpy.zeros((nRows-1,len(newBaseList)))
	Cb=numpy.zeros((1,len(baseList)))
	for e in newBaseList:
		matrixB[:,count]=ttable[1:,e]
		count+=1
	count=0
	for e in newNonBaseList:
		matrixN[:,count]=ttable[1:,e]
		count+=1
	Cb=numpy.zeros((1,len(baseList)))
	count=0
	for i in baseList:
		Cb[0,count]=coefficientList[i]
		count+=1
	Cb=Cb.transpose()
	for i in range(0,len(newNonBaseList)):
		Costb=coefficientList[newNonBaseList[i]]
		zb=numpy.dot(Cb.transpose(),ttable[1:,newNonBaseList[i]])
		ttable[0,newNonBaseList[i]]=Costb-zb
	ttable[0,nCols-1]=0-numpy.dot(Cb.transpose(),ttable[1:,nCols-1])
	#super gambiarra pra tratar os erros de floating point do python
	for i in range(0,ttable.shape[0]):
		for j in range(0,ttable.shape[1]):
			if ttable[i][j]<=0.00000001 and ttable[i][j]>=-0.00000001 and ttable[i][j]!=0:
				ttable[i][j]=0
	return ttable,newNonBaseList,newBaseList,matrixA,coefficientList

#funcao que imprime os valores dos x originais de acordo com a tabela
def extractSolutionVertex(ttable,baseList,n):
	v=[]
	for i in range(0,n):
		if i in baseList:
			v.append(ttable[baseList.index(i)+1,len(ttable[0])-1])
		else:
			v.append(0)
	return v

#TODO
def findDirection(n,ttable,nbList,baseList,b):
	pass

#funcao para "andar" um vertice caso haja multiplas solucoes
def findNextVertex(n,ttable,nbList,baseList,b):
	baseList,nbList,ttable=modifiedSimplexStep(baseList=list(baseList),nBaseList=list(nbList),ttable=ttable.copy(),b=b.copy(),ftype=2)
	v=extractSolutionVertex(ttable=ttable.copy(),baseList=list(baseList),n=n)
	return v


#funcao que controla a execucao do simplex
def doTheSimplex(n,m,problemType,coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions,RHS):
	keepGoing=True
	originalType=problemType
	problemType="min"
	BaseList=pickBasicsPhase1(n=n,m=m,coefficientList=list(coefficientList),restrictionTypeList=list(restrictionTypeList))
	nonBaseList=range(0,len(coefficientList))
	for e in BaseList: nonBaseList.remove(e)
	nArtificial=restrictionTypeList.count(">")+restrictionTypeList.count("=")
	firstTable=generateFirstTable(n=n,m=m,nA=nArtificial,baseList=list(BaseList),coefficientList=list(coefficientList),restrictionCoefficientMatrix=restrictionCoefficientMatrix.copy(),RHS=RHS.copy())
	artificialCoefficientList=numpy.zeros(len(coefficientList)+1)
	for i in range(2,nArtificial+2):
		artificialCoefficientList[len(artificialCoefficientList)-i]=1
	ttable=firstTable.copy()
	printSimplexTable(ttable)
	while keepGoing==True:
		BaseList,nonBaseList,ttable,keepGoing=simplexStep(baseList=list(BaseList),nBaseList=list(nonBaseList),ttable=ttable,b=RHS.copy())
	if min(ttable[0][:len(ttable[0])-1])<0 or max(ttable[0][:len(ttable[0])-1])!=1:
		print("5")
		print("imp")
		return 0
	ttable,nonBaseList,BaseList,restrictionCoefficientMatrix,coefficientList =makeTablePhase2(ttable=ttable.copy(),baseList=list(BaseList),nBaseList=list(nonBaseList),nArtificial=nArtificial,coefficientList=list(coefficientList),matrixA=restrictionCoefficientMatrix.copy())
	printSimplexTable(ttable)
	keepGoing=True
	while keepGoing==True:
		BaseList,nonBaseList,ttable,keepGoing=simplexStep(baseList=list(BaseList),nBaseList=list(nonBaseList),ttable=ttable,b=RHS.copy())
	isgood=True
	for e in nonBaseList:
		if ttable[0][e]<0 and (ttable[:,e]<=0).all():
			isgood=False
			print("4")
			if(originalType=="max"): 
				print("+ inf")
			else: 
				print("- inf")
			break
		if ttable[0][e]==0:
			isgood=False
			if(ttable[:,e]<=0).all():
				print("3")
				vertexI=extractSolutionVertex(ttable=ttable.copy(),baseList=list(BaseList),n=n)
				#findDirection(n=n,ttable=ttable.copy(),nbList=list(nonBaseList),baseList=list(BaseList),b=RHS.copy())
				printVertex(vertex=vertexI,i=1)
				print("%0.4f"%(ttable[0][len(ttable[0])-1]*-1))
			else:
				print("2")
				vertex1=extractSolutionVertex(ttable=ttable.copy(),baseList=list(BaseList),n=n)
				vertex2=findNextVertex(n=n,ttable=ttable.copy(),nbList=list(nonBaseList),baseList=list(BaseList),b=RHS.copy())
				printVertex(vertex=vertex1,i=1)
				printVertex(vertex=vertex2,i=2)
				print("%0.4f"%(ttable[0][len(ttable[0])-1]*-1))
			break
	if isgood:
		print("1")
		printVertex(vertex=extractSolutionVertex(ttable=ttable.copy(),baseList=list(BaseList),n=n),i=1)
		print("%0.4f"%(ttable[0][len(ttable[0])-1]*-1))




#funcao main
def main():
		nProblems=int(raw_input("")) #le a primeira linha contendo o numero de problemas
		for i in range(0,nProblems):
			print("- - -")
			n,m,problemType,coefficientList,restrictionCoefficientMatrix,restrictionTypeList,RHS,varRestrictions=readlines()
			restrictionTypeListCOPY=list(restrictionTypeList)
			coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions=padronize(n=n,m=m,problemType=problemType,coefficientList=coefficientList,restrictionCoefficientMatrix=restrictionCoefficientMatrix,restrictionTypeList=restrictionTypeList,varRestrictions=varRestrictions)
			coefficientList,restrictionCoefficientMatrix,restrictionTypeList,varRestrictions=AddArtificialVariable(n=n,m=m,coefficientList=coefficientList,restrictionCoefficientMatrix=restrictionCoefficientMatrix,restrictionTypeList=list(restrictionTypeListCOPY),varRestrictions=varRestrictions)
			doTheSimplex(n=n,m=m,problemType=problemType,coefficientList=coefficientList,restrictionCoefficientMatrix=restrictionCoefficientMatrix,restrictionTypeList=restrictionTypeListCOPY,varRestrictions=varRestrictions,RHS=RHS)
main()